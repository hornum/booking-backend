from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.users.models import User
from booking.infra.a_security import decode_access_token
from booking.infra.db import async_session_factory
from booking.infra.users.repository import SqlUserRepository

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = decode_access_token(token)
    except InvalidTokenError:
        raise cred_exc from None

    user_repo = SqlUserRepository(session)
    user = await user_repo.get(user_id)

    if user is None:
        raise cred_exc

    return user


async def get_payment_provider() -> PaymentProvider:
    return FakePaymentProvider()

