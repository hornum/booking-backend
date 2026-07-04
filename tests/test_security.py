from booking.infra.a_security import hash_password, verify_password, hash_token, create_access_token, \
    decode_access_token


async def test_pass_hash_verify_succ():
    password = "testpass"
    hashed = await hash_password(password)
    assert await verify_password(password, hashed) == True


async def test_pass_hash_verify_fail():
    hashed = await hash_password("testpass")
    assert await verify_password("wrong_pass", hashed) == False


def test_access_token_success():
    user_id = 12
    token = create_access_token(user_id=user_id)
    assert decode_access_token(token) == user_id
