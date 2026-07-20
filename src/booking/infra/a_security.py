import asyncio
import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from config.config import settings

pwd_context = CryptContext(schemes=settings.PASS_ALGORITHMS, deprecated="auto")


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(pwd_context.hash, password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def verify_password(plain: str, hashed: str) -> bool:
    return await asyncio.to_thread(pwd_context.verify, plain, hashed)


def create_access_token(user_id: int, expire: datetime | None = None) -> str:
    if expire is None:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM
    )


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
    )
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise jwt.InvalidTokenError()
    try:
        user_id_int = int(user_id_str)
    except ValueError:
        raise jwt.InvalidTokenError() from None

    return user_id_int
