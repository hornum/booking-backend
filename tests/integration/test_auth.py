import pytest

from booking.domain.users.errors import UserNotFound
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
