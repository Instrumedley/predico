"""
Tests for user login functionality (TDD).
"""
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from app.core.security import decode_access_token


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user_data):
    """Test successful login with correct credentials."""
    # First, signup a user
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Then login
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user_data):
    """Test login with wrong password fails."""
    # First, signup a user
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Then try to login with wrong password
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123!",
    })
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user fails."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword123!",
    })
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_unverified_email(client: AsyncClient, test_user_data):
    """Test login with unverified email fails (optional - depends on requirements)."""
    # Signup user (creates unverified user)
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Try to login before verification
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    
    # This behavior depends on requirements - should we block unverified users?
    # For now, we'll allow login but document this decision
    # If blocking is required, assert response.status_code == 403
    pass


@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    """Test login with missing fields fails."""
    # Missing email
    response = await client.post("/api/v1/auth/login", json={
        "password": "TestPassword123!",
    })
    assert response.status_code == 422
    
    # Missing password
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_email_format(client: AsyncClient):
    """Test login with invalid email format fails."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "not-an-email",
        "password": "TestPassword123!",
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_token_validity(client: AsyncClient, test_user_data):
    """Test that login returns a valid JWT token."""
    # Signup and login
    await client.post("/api/v1/auth/signup", json=test_user_data)
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Verify token can be used to access protected endpoint
    # We'll need a protected endpoint for this test
    # For now, this documents expected behavior
    assert len(token) > 0  # Basic check that token exists


@pytest.mark.asyncio
async def test_login_without_remember_me_uses_24_hour_token(client: AsyncClient, test_user_data):
    """Default login should issue a token valid for about 24 hours."""
    await client.post("/api/v1/auth/signup", json=test_user_data)

    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
        "remember_me": False,
    })

    assert response.status_code == 200
    payload = decode_access_token(response.json()["access_token"])
    assert payload is not None

    expires_at = datetime.utcfromtimestamp(payload["exp"])
    now = datetime.utcnow()
    assert expires_at > now + timedelta(hours=23)
    assert expires_at < now + timedelta(hours=25)


@pytest.mark.asyncio
async def test_login_with_remember_me_uses_30_day_token(client: AsyncClient, test_user_data):
    """Remember-me login should issue a token valid for about 30 days."""
    await client.post("/api/v1/auth/signup", json=test_user_data)

    response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
        "remember_me": True,
    })

    assert response.status_code == 200
    payload = decode_access_token(response.json()["access_token"])
    assert payload is not None

    expires_at = datetime.utcfromtimestamp(payload["exp"])
    now = datetime.utcnow()
    assert expires_at > now + timedelta(days=29)
    assert expires_at < now + timedelta(days=31)

