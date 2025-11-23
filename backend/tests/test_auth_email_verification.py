"""
Tests for email verification functionality (TDD).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient, test_user_data):
    """Test successful email verification with valid token."""
    # Signup user
    signup_response = await client.post("/api/v1/auth/signup", json=test_user_data)
    assert signup_response.status_code == 201
    
    # Get verification token (in real implementation, this comes from email)
    # For testing, we'll need a way to get the token
    # This might require a test endpoint or database access
    
    # Verify email
    verification_token = "valid_verification_token"  # Will be mocked/retrieved in implementation
    response = await client.post("/api/v1/auth/verify-email", json={
        "token": verification_token,
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "verified" in data["message"].lower() or "success" in data["message"].lower()


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    """Test email verification with invalid token fails."""
    response = await client.post("/api/v1/auth/verify-email", json={
        "token": "invalid_token_12345",
    })
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_expired_token(client: AsyncClient):
    """Test email verification with expired token fails."""
    # Create an expired token (implementation will handle this)
    expired_token = "expired_verification_token"
    response = await client.post("/api/v1/auth/verify-email", json={
        "token": expired_token,
    })
    
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_already_verified(client: AsyncClient, test_user_data):
    """Test verifying an already verified email."""
    # Signup and verify
    await client.post("/api/v1/auth/signup", json=test_user_data)
    # ... verify email first time ...
    
    # Try to verify again
    verification_token = "already_used_token"
    response = await client.post("/api/v1/auth/verify-email", json={
        "token": verification_token,
    })
    
    # Should either succeed (idempotent) or return appropriate message
    # This depends on implementation decision
    assert response.status_code in [200, 400]


@pytest.mark.asyncio
async def test_verify_email_missing_token(client: AsyncClient):
    """Test email verification with missing token fails."""
    response = await client.post("/api/v1/auth/verify-email", json={})
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_resend_verification_email(client: AsyncClient, test_user_data):
    """Test resending verification email."""
    # Signup user
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Request resend
    response = await client.post("/api/v1/auth/resend-verification", json={
        "email": test_user_data["email"],
    })
    
    assert response.status_code == 200
    assert "sent" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_resend_verification_nonexistent_email(client: AsyncClient):
    """Test resending verification to non-existent email."""
    response = await client.post("/api/v1/auth/resend-verification", json={
        "email": "nonexistent@example.com",
    })
    
    # Should either return 404 or 200 (for security, don't reveal if email exists)
    # Common practice is to return 200 to prevent email enumeration
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_resend_verification_already_verified(client: AsyncClient, test_user_data):
    """Test resending verification to already verified email."""
    # Signup, verify, then try to resend
    await client.post("/api/v1/auth/signup", json=test_user_data)
    # ... verify email ...
    
    response = await client.post("/api/v1/auth/resend-verification", json={
        "email": test_user_data["email"],
    })
    
    # Should return appropriate message (either success or "already verified")
    assert response.status_code in [200, 400]

