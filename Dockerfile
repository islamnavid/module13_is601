
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies as root
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade Python packaging tools
RUN python -m pip install --no-cache-dir --upgrade \
    pip "setuptools>=78.1.1" wheel

# Install Python dependencies
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user and set permissions
RUN groupadd -r appgroup && \
    useradd -r -g appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Application health check
HEALTHCHECK --interval=30s --timeout=30s \
    --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Initialize database and start FastAPI
CMD ["sh", "-c", "python -m app.database_init && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
