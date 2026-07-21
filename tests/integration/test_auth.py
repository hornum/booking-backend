from datetime import UTC, datetime

import pytest

from booking.domain.refresh_token.models import RefreshToken
from booking.domain.users.errors import UserNotFound
from booking.domain.users.models import User
from booking.infra.a_security import hash_token
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.auth import login_user


async def test_reg_login_success(client, auth_json_data):
    response = await client.post("/v1/auth/register", json=auth_json_data)
    assert response.status_code == 200
    response = await client.post("/v1/auth/login", data=auth_json_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


async def test_login_missing_username_fail(session):
    user_repo = SqlUserRepository(session)
    token_repo = SqlTokenRepository(session)

    with pytest.raises(UserNotFound):
        await login_user(
            user_repo=user_repo,
            token_repo=token_repo,
            username="wrong_username",
            password="long_password",
        )


async def test_get_current_user(client, auth_json_data):
    user = await client.post("/v1/auth/register", json=auth_json_data)
    data = user.json()
    response = await client.get(
        "/v1/user/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["email"] == auth_json_data["email"]
    assert response_data["username"] == auth_json_data["username"]
    assert response_data["id"]


async def test_token_refresh_success(client, refresh_token_json_data):
    first_response = await client.post("/v1/auth/refresh", json=refresh_token_json_data)
    assert first_response.status_code == 200

    sec_response = await client.post("/v1/auth/refresh", json=refresh_token_json_data)
    assert sec_response.status_code == 401


async def test_token_refresh_not_found_fail(client):
    response = await client.post(
        "/v1/auth/refresh", json={"refresh_token": "wrong_token"}
    )
    assert response.status_code == 401


async def test_token_refresh_expired_fail(session, client):
    token_repo = SqlTokenRepository(session)
    user_repo = SqlUserRepository(session)
    user = await user_repo.add(
        User(
            username="testuser",
            email="testuser@test.test",
            hashed_password="123",
        )
    )
    await token_repo.add(
        RefreshToken(
            token_hash=hash_token("test_token"),
            user_id=user.id,
            expires_at=datetime(year=2021, month=1, day=1, tzinfo=UTC),
            created_at=datetime.now(UTC),
        )
    )
    response = await client.post(
        "/v1/auth/refresh", json={"refresh_token": "test_token"}
    )
    assert response.status_code == 401


async def test_refresh_token_reuse_revokes_all_user_tokens(
    session, client, active_refresh_token_family
):
    response = await client.post(
        "/v1/auth/refresh", json={"refresh_token": active_refresh_token_family.first}
    )
    assert response.status_code == 200

    response = await client.post(
        "/v1/auth/refresh", json={"refresh_token": active_refresh_token_family.first}
    )
    assert response.status_code == 401
    # Test session override does not commit after each HTTP request.
    # Commit explicitly to persist revoke_all before the next request.
    await session.commit()

    response = await client.post(
        "/v1/auth/refresh", json={"refresh_token": active_refresh_token_family.second}
    )
    assert response.status_code == 401
