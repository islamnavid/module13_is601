
import re
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:8000"
VALID_PASSWORD = "TestPass123!"


def unique_user():
    suffix = uuid4().hex[:12]
    return {
        "username": f"navid_{suffix}",
        "email": f"navid_{suffix}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": VALID_PASSWORD,
    }


def fill_registration(page: Page, user: dict):
    page.goto(f"{BASE_URL}/register")

    page.locator("#username").fill(user["username"])
    page.locator("#email").fill(user["email"])
    page.locator("#first_name").fill(user["first_name"])
    page.locator("#last_name").fill(user["last_name"])
    page.locator("#password").fill(user["password"])
    page.locator("#confirm_password").fill(user["password"])


def register_user(page: Page, user: dict):
    fill_registration(page, user)

    with page.expect_response(
        lambda response: (
            "/auth/register" in response.url
            and response.request.method == "POST"
        )
    ) as response_info:
        page.get_by_role("button", name="Register").click()

    assert response_info.value.status == 201
    expect(page.locator("#successMessage")).to_contain_text(
        "Registration successful"
    )


@pytest.mark.e2e
def test_successful_registration(page: Page):
    """A valid user can register through the browser."""
    user = unique_user()
    register_user(page, user)

    expect(page).to_have_url(re.compile(r"/login$"), timeout=5000)


@pytest.mark.e2e
def test_successful_login_and_jwt_storage(page: Page):
    """A registered user can log in and receive JWT tokens."""
    user = unique_user()
    register_user(page, user)

    page.goto(f"{BASE_URL}/login")
    page.locator("#username").fill(user["username"])
    page.locator("#password").fill(user["password"])

    with page.expect_response(
        lambda response: (
            "/auth/login" in response.url
            and response.request.method == "POST"
        )
    ) as response_info:
        page.get_by_role("button", name="Sign in").click()

    assert response_info.value.status == 200

    expect(page).to_have_url(
        re.compile(r"/dashboard$"), timeout=5000
    )

    access_token = page.evaluate(
        "() => localStorage.getItem('access_token')"
    )
    refresh_token = page.evaluate(
        "() => localStorage.getItem('refresh_token')"
    )
    stored_username = page.evaluate(
        "() => localStorage.getItem('username')"
    )

    assert access_token, "Access token was not stored"
    assert refresh_token, "Refresh token was not stored"
    assert stored_username == user["username"]

    expect(page.get_by_text(user["username"])).to_be_visible()


@pytest.mark.e2e
def test_registration_rejects_short_password(page: Page):
    """Client-side validation rejects a short password."""
    user = unique_user()
    user["password"] = "abc"

    fill_registration(page, user)

    page.get_by_role("button", name="Register").click()

    expect(page.locator("#errorMessage")).to_contain_text(
        "Password must be at least 8 characters long"
    )
    expect(page).to_have_url(re.compile(r"/register$"))


@pytest.mark.e2e
def test_login_rejects_wrong_password(page: Page):
    """An incorrect password displays an error."""
    user = unique_user()
    register_user(page, user)

    page.goto(f"{BASE_URL}/login")
    page.locator("#username").fill(user["username"])
    page.locator("#password").fill("WrongPass123!")

    with page.expect_response(
        lambda response: (
            "/auth/login" in response.url
            and response.request.method == "POST"
        )
    ) as response_info:
        page.get_by_role("button", name="Sign in").click()

    assert response_info.value.status == 401

    expect(page.locator("#errorMessage")).to_contain_text(
        "Invalid username or password"
    )
    expect(page).to_have_url(re.compile(r"/login$"))

    access_token = page.evaluate(
        "() => localStorage.getItem('access_token')"
    )
    assert access_token is None
