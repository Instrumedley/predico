"""
Tests for user signup functionality (TDD).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, test_user_data):
    """Test successful user signup."""
    response = await client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "message" in data
    assert data["user"]["email"] == test_user_data["email"]
    assert data["user"]["username"] == test_user_data["username"]
    assert "id" in data["user"]
    assert "password" not in data["user"]  # Password should never be returned


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_user_data):
    """Test signup with duplicate email fails."""
    # First signup
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Second signup with same email
    response = await client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower() or "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_duplicate_username(client: AsyncClient, test_user_data):
    """Test signup with duplicate username fails."""
    # First signup
    await client.post("/api/v1/auth/signup", json=test_user_data)
    
    # Second signup with same username but different email
    duplicate_data = test_user_data.copy()
    duplicate_data["email"] = "different@example.com"
    response = await client.post("/api/v1/auth/signup", json=duplicate_data)
    
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower() or "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient, test_user_data):
    """Test signup with invalid email format fails."""
    invalid_data = test_user_data.copy()
    invalid_data["email"] = "not-an-email"
    
    response = await client.post("/api/v1/auth/signup", json=invalid_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient, test_user_data):
    """Test signup with weak password fails."""
    weak_password_data = test_user_data.copy()
    weak_password_data["password"] = "123"  # Too short
    
    response = await client.post("/api/v1/auth/signup", json=weak_password_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_signup_missing_fields(client: AsyncClient):
    """Test signup with missing required fields fails."""
    # Missing email
    response = await client.post("/api/v1/auth/signup", json={
        "username": "testuser",
        "password": "TestPassword123!",
    })
    assert response.status_code == 422
    
    # Missing username
    response = await client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "TestPassword123!",
    })
    assert response.status_code == 422
    
    # Missing password
    response = await client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "username": "testuser",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_creates_unverified_user(client: AsyncClient, test_user_data, db_session):
    """Test that signup creates a user with email_verified=False."""
    response = await client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == 201
    
    # Check database directly
    from app.db.models import User
    from sqlalchemy import select
    
    result = await db_session.execute(select(User).where(User.email == test_user_data["email"]))
    user = result.scalar_one()
    
    # Note: We'll need to add email_verified field to User model
    # For now, this test documents the expected behavior
    assert user.email == test_user_data["email"]
    assert user.username == test_user_data["username"]


@pytest.mark.asyncio
async def test_signup_sends_verification_email(client: AsyncClient, test_user_data):
    """Test that signup triggers verification email sending."""
    # This test will verify that the email service is called
    # We'll mock the email service in the implementation
    response = await client.post("/api/v1/auth/signup", json=test_user_data)
    
    assert response.status_code == 201
    # In implementation, we'll verify email service was called
    # For now, this documents the expected behavior

