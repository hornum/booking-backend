from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session
from booking.api.schemas.auth import UserRegister, AuthResponse
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.auth import register_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
async def register(data: UserRegister, session: AsyncSession = Depends(get_session)):
    user_repo = SqlUserRepository(session)
    token_repo = SqlTokenRepository(session)
    return await register_user(
        user_repo=user_repo,
        token_repo=token_repo,
        username=data.username,
        email=str(data.email),
        password=data.password,
    )


# @router.post("/login", response_model=TokenResponse)
# @limiter.limit("5/minute")
# async def login(
#     data: Annotated[OAuth2PasswordRequestForm, Depends()],
#     db: db_dependency,
#     request: Request,
# ):
#     return await login_user(db, data.username, data.password)
#
#
# @router.post("/refresh", response_model=TokenPair)
# async def refresh(body: RefreshRequest, db: db_dependency):
#     return await refresh_tokens(db, body.refresh_token)
#
#
# @router.post("/logout")
# async def logout(body: RefreshRequest, db: db_dependency):
#     await logout_user(db, body.refresh_token)
#     return {"message": "Successfully logged out"}
#
#
# @router.get("/verify")
# async def verify(db: db_dependency, token: str) -> dict:
#     await verify_email_token(db, token)
#     return {"message": "Email verified"}
