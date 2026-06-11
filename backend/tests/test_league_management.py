"""Tests for league creator management (remove member, lock/unlock joins)."""
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
async def test_creator_can_remove_member(client: AsyncClient):
    creator_token = await _signup_and_login(client, "creator@example.com", "creator")
    member_token = await _signup_and_login(client, "member@example.com", "member")

    create_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Friends League", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    assert create_response.status_code == 201
    league_id = create_response.json()["id"]

    join_response = await client.post(
        f"/api/v1/leagues/{league_id}/join",
        json={},
        headers=_auth_headers(member_token),
    )
    assert join_response.status_code == 200

    detail_response = await client.get(
        f"/api/v1/leagues/{league_id}",
        headers=_auth_headers(creator_token),
    )
    member_user_id = next(
        entry["user_id"]
        for entry in detail_response.json()["rankings"]
        if entry["username"] == "member"
    )

    remove_response = await client.delete(
        f"/api/v1/leagues/{league_id}/members/{member_user_id}",
        headers=_auth_headers(creator_token),
    )
    assert remove_response.status_code == 200
    data = remove_response.json()
    assert data["member_count"] == 1
    assert all(entry["username"] != "member" for entry in data["rankings"])

    member_detail = await client.get(
        f"/api/v1/leagues/{league_id}",
        headers=_auth_headers(member_token),
    )
    assert member_detail.json()["is_member"] is False


@pytest.mark.asyncio
async def test_non_creator_cannot_remove_member(client: AsyncClient):
    creator_token = await _signup_and_login(client, "owner@example.com", "owner")
    member_token = await _signup_and_login(client, "player@example.com", "player")
    other_token = await _signup_and_login(client, "other@example.com", "other")

    create_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Locked Down", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    league_id = create_response.json()["id"]

    await client.post(
        f"/api/v1/leagues/{league_id}/join",
        json={},
        headers=_auth_headers(member_token),
    )
    await client.post(
        f"/api/v1/leagues/{league_id}/join",
        json={},
        headers=_auth_headers(other_token),
    )

    detail_response = await client.get(
        f"/api/v1/leagues/{league_id}",
        headers=_auth_headers(creator_token),
    )
    member_user_id = next(
        entry["user_id"]
        for entry in detail_response.json()["rankings"]
        if entry["username"] == "player"
    )

    remove_response = await client.delete(
        f"/api/v1/leagues/{league_id}/members/{member_user_id}",
        headers=_auth_headers(other_token),
    )
    assert remove_response.status_code == 403


@pytest.mark.asyncio
async def test_creator_cannot_remove_self(client: AsyncClient):
    creator_token = await _signup_and_login(client, "solo@example.com", "solo")

    create_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Solo League", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    league_id = create_response.json()["id"]

    detail_response = await client.get(
        f"/api/v1/leagues/{league_id}",
        headers=_auth_headers(creator_token),
    )
    creator_user_id = detail_response.json()["rankings"][0]["user_id"]

    remove_response = await client.delete(
        f"/api/v1/leagues/{league_id}/members/{creator_user_id}",
        headers=_auth_headers(creator_token),
    )
    assert remove_response.status_code == 400


@pytest.mark.asyncio
async def test_lock_prevents_join_and_invites(client: AsyncClient):
    creator_token = await _signup_and_login(client, "host@example.com", "host")
    guest_token = await _signup_and_login(client, "guest@example.com", "guest")

    create_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Closed League", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    league_id = create_response.json()["id"]

    lock_response = await client.post(
        f"/api/v1/leagues/{league_id}/lock",
        headers=_auth_headers(creator_token),
    )
    assert lock_response.status_code == 200
    assert lock_response.json()["is_join_locked"] is True

    join_response = await client.post(
        f"/api/v1/leagues/{league_id}/join",
        json={},
        headers=_auth_headers(guest_token),
    )
    assert join_response.status_code == 403

    invite_response = await client.post(
        f"/api/v1/leagues/{league_id}/invitations",
        json={"emails": ["guest@example.com"]},
        headers=_auth_headers(creator_token),
    )
    assert invite_response.status_code == 403


@pytest.mark.asyncio
async def test_unlock_allows_join_again(client: AsyncClient):
    creator_token = await _signup_and_login(client, "reopen@example.com", "reopen")
    guest_token = await _signup_and_login(client, "joiner@example.com", "joiner")

    create_response = await client.post(
        "/api/v1/leagues",
        json={"name": "Reopen League", "is_private": False},
        headers=_auth_headers(creator_token),
    )
    league_id = create_response.json()["id"]

    await client.post(f"/api/v1/leagues/{league_id}/lock", headers=_auth_headers(creator_token))

    unlock_response = await client.post(
        f"/api/v1/leagues/{league_id}/unlock",
        headers=_auth_headers(creator_token),
    )
    assert unlock_response.status_code == 200
    assert unlock_response.json()["is_join_locked"] is False

    join_response = await client.post(
        f"/api/v1/leagues/{league_id}/join",
        json={},
        headers=_auth_headers(guest_token),
    )
    assert join_response.status_code == 200
