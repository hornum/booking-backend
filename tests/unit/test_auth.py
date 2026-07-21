from dataclasses import asdict

import pytest

from booking.domain.users.errors import (
    IncorrectPassword,
    InvalidUserEmail,
    UserAlreadyExists,
    UserNotFound,
)
from booking.domain.users.models import User
from booking.service.auth import (
    ReuseDetected,
    login_user,
    refresh_tokens,
    register_user,
)


async def test_correct_auth(auth_json_data, user_repo, token_repo):
    response = await register_user(
        user_repo=user_repo,
        token_repo=token_repo,
        **auth_json_data,
    )

    json = asdict(response)

    assert "access_token" in json
    assert "refresh_token" in json


async def test_user_exists_err(auth_json_data, user_repo, token_repo):
    same_name_data = {**auth_json_data, "email": "jhon@test.com"}
    same_mail_data = {**auth_json_data, "username": "Jhon"}
    print(same_name_data)
    print(same_mail_data)
    print(auth_json_data)

    await register_user(
        user_repo=user_repo,
        token_repo=token_repo,
        **auth_json_data,
    )

    with pytest.raises(UserAlreadyExists):
        await register_user(
            user_repo=user_repo,
            token_repo=token_repo,
            **same_name_data,
        )

    with pytest.raises(UserAlreadyExists):
        await register_user(
            user_repo=user_repo,
            token_repo=token_repo,
            **same_mail_data,
        )


async def test_login(auth_json_data, user_repo, token_repo):
    await register_user(user_repo=user_repo, token_repo=token_repo, **auth_json_data)

    response = await login_user(
        user_repo=user_repo,
        token_repo=token_repo,
        username=auth_json_data["username"],
        password=auth_json_data["password"],
    )

    assert response.access_token
    assert response.refresh_token
    assert response.user_id


async def test_login_fail(auth_json_data, user_repo, token_repo):
    await register_user(user_repo=user_repo, token_repo=token_repo, **auth_json_data)

    with pytest.raises(IncorrectPassword):
        await login_user(
            user_repo=user_repo,
            token_repo=token_repo,
            username=auth_json_data["username"],
            password="wrong_password",
        )

    with pytest.raises(UserNotFound):
        await login_user(
            user_repo=user_repo,
            token_repo=token_repo,
            username="wrong_name",
            password=auth_json_data["password"],
        )


async def test_token_refreshes(auth_json_data, user_repo, token_repo):
    tokens = await register_user(
        user_repo=user_repo, token_repo=token_repo, **auth_json_data
    )

    refreshed = await refresh_tokens(
        token_repo=token_repo, refresh_token=tokens.refresh_token
    )

    assert refreshed.access_token
    assert refreshed.refresh_token
    assert refreshed.user_id

    response = await refresh_tokens(
        token_repo=token_repo, refresh_token=tokens.refresh_token
    )
    assert isinstance(response, ReuseDetected)


def test_email_not_empty():
    with pytest.raises(InvalidUserEmail):
        User(
            id=1,
            username="a123",
            hashed_password="123531",
            email="",
        )


def test_invalid_email():
    with pytest.raises(InvalidUserEmail):
        User(
            id=1,
            username="a123",
            hashed_password="123531",
            email="test$test.com",
        )
