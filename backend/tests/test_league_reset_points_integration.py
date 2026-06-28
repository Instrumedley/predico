"""Integration tests for reset-on-join league scoring."""
import pytest
from httpx import AsyncClient


async def _signup_and_login(client: AsyncClient, email: str, username: str) -> str:
    password = "TestPassword123!"
    await client.post(
        "/api/v1/auth/signup",
        json={"email": email, "username": username, "password": password},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_league_with_members_start_at_zero(client: AsyncClient):
    creator_token = await _signup_and_login(client, "fresh@example.com", "freshstarter")

    create_response = await client.post(
        "/api/v1/leagues",
        json={
            "name": "Fresh Start League",
            "is_private": False,
            "members_start_at_zero": True,
        },
        headers=_auth_headers(creator_token),
    )
    assert create_response.status_code == 201
    data = create_response.json()
    assert data["members_start_at_zero"] is True

    detail_response = await client.get(
        f"/api/v1/leagues/{data['id']}",
        headers=_auth_headers(creator_token),
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["members_start_at_zero"] is True
    assert detail["rankings"][0]["total_points"] == 0


@pytest.mark.asyncio
async def test_reset_league_does_not_affect_regular_league(client: AsyncClient):
    creator_token = await _signup_and_login(client, "dual@example.com", "dualleague")

    regular_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Regular League", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    reset_response = await client.post(
        "/api/v1/leagues",
        json={
            "name": "Reset League",
            "is_private": False,
            "members_start_at_zero": True,
        },
        headers=_auth_headers(creator_token),
    )
    assert regular_response.status_code == 201
    assert reset_response.status_code == 201

    regular_detail = await client.get(
        f"/api/v1/leagues/{regular_response.json()['id']}",
        headers=_auth_headers(creator_token),
    )
    reset_detail = await client.get(
        f"/api/v1/leagues/{reset_response.json()['id']}",
        headers=_auth_headers(creator_token),
    )

    assert regular_detail.json()["members_start_at_zero"] is False
    assert reset_detail.json()["members_start_at_zero"] is True
    assert regular_detail.json()["rankings"][0]["total_points"] == 0
    assert reset_detail.json()["rankings"][0]["total_points"] == 0
