"""
Tests for password reset functionality (TDD).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_password_reset_success(client: AsyncClient, test_user_data):
    """Test successful password reset request."""
    # Signup user
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Request password reset
    response = await client.post("/api/v1/auth/forgot-password", json={
        "email": test_user_data["email"],
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "sent" in data["message"].lower() or "reset" in data["message"].lower()


@pytest.mark.asyncio
async def test_request_password_reset_nonexistent_email(client: AsyncClient):
    """Test password reset request for non-existent email."""
    response = await client.post("/api/v1/auth/forgot-password", json={
        "email": "nonexistent@example.com",
    })
    
    # For security, should return 200 (don't reveal if email exists)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_success(client: AsyncClient, test_user_data):
    """Test successful password reset with valid token."""
    # Signup user
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Request reset (gets token)
    await client.post("/api/v1/auth/forgot-password", json={
        "email": test_user_data["email"],
    })
    
    # Reset password with token
    reset_token = "valid_reset_token"  # Will be retrieved/mocked in implementation
    new_password = "NewPassword123!"
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_password,
    })
    
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower() or "reset" in response.json()["message"].lower()
    
    # Verify can login with new password
    login_response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": new_password,
    })
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    """Test password reset with invalid token fails."""
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "invalid_token_12345",
        "new_password": "NewPassword123!",
    })
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_expired_token(client: AsyncClient):
    """Test password reset with expired token fails."""
    expired_token = "expired_reset_token"
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": expired_token,
        "new_password": "NewPassword123!",
    })
    
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_weak_password(client: AsyncClient, test_user_data):
    """Test password reset with weak password fails."""
    await client.post("/api/v1/auth/signup", json=test_user_data)
    await client.post("/api/v1/auth/forgot-password", json={
        "email": test_user_data["email"],
    })
    
    reset_token = "valid_reset_token"
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": "123",  # Too weak
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_reset_password_missing_fields(client: AsyncClient):
    """Test password reset with missing fields fails."""
    # Missing token
    response = await client.post("/api/v1/auth/reset-password", json={
        "new_password": "NewPassword123!",
    })
    assert response.status_code == 422
    
    # Missing password
    response = await client.post("/api/v1/auth/reset-password", json={
        "token": "some_token",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_password_old_password_invalidated(client: AsyncClient, test_user_data):
    """Test that after password reset, old password no longer works."""
    # Signup and login with original password
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Request and complete password reset
    await client.post("/api/v1/auth/forgot-password", json={
        "email": test_user_data["email"],
    })
    reset_token = "valid_reset_token"
    new_password = "NewPassword123!"
    await client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_password,
    })
    
    # Try to login with old password (should fail)
    login_response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],  # Old password
    })
    assert login_response.status_code == 401
    
    # Login with new password (should succeed)
    login_response = await client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": new_password,
    })
    assert login_response.status_code == 200

