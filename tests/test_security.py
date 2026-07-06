from booking.infra.a_security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


async def test_pass_hash_verify_succ():
    password = "testpass"
    hashed = await hash_password(password)
    assert await verify_password(password, hashed)


async def test_pass_hash_verify_fail():
    hashed = await hash_password("testpass")
    assert not await verify_password("wrong_pass", hashed)


def test_access_token_success():
    user_id = 12
    token = create_access_token(user_id=user_id)
    assert decode_access_token(token) == user_id
