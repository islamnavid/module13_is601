
# app/auth/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import UUID
import secrets

import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.auth.redis import is_blacklisted
from app.schemas.token import TokenType
from app.database import get_db
from app.models.user import User


settings = get_settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_token(
    user_id: Union[str, UUID],
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access or refresh token."""

    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    elif token_type == TokenType.ACCESS:
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire = now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    if isinstance(user_id, UUID):
        user_id = str(user_id)

    to_encode = {
        "sub": user_id,
        "type": token_type.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(16),
    }

    secret = (
        settings.JWT_SECRET_KEY
        if token_type == TokenType.ACCESS
        else settings.JWT_REFRESH_SECRET_KEY
    )

    try:
        return jwt.encode(
            to_encode,
            secret,
            algorithm=settings.ALGORITHM,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create token: {exc}",
        ) from exc


async def decode_token(
    token: str,
    token_type: TokenType,
    verify_exp: bool = True,
) -> dict[str, Any]:
    """Decode and verify a JWT token."""

    secret = (
        settings.JWT_SECRET_KEY
        if token_type == TokenType.ACCESS
        else settings.JWT_REFRESH_SECRET_KEY
    )

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_exp": verify_exp,
                "require": ["sub", "type", "jti", "iat", "exp"],
            },
        )

        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if await is_blacklisted(payload["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from an access token."""

    try:
        payload = await decode_token(token, TokenType.ACCESS)
        user_id = payload["sub"]

        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        return user

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
