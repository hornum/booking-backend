from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session
from booking.api.schemas.auth import UserRegister, AuthResponse, LoginResponse
from booking.domain.users.errors import UserAlreadyExists
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.auth import register_user, login_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register")
async def register(data: UserRegister, session: AsyncSession = Depends(get_session)) -> AuthResponse:
    user_repo = SqlUserRepository(session)
    token_repo = SqlTokenRepository(session)
    try:
        user = await register_user(
            user_repo=user_repo,
            token_repo=token_repo,
            username=data.username,
            email=str(data.email),
            password=data.password,
        )
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="User already exists")

    return AuthResponse(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        user_id=user.user_id,
    )


@router.post("/login")
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    user_repo = SqlUserRepository(session)
    token_repo = SqlTokenRepository(session)
    user = await login_user(
        user_repo=user_repo,
        token_repo=token_repo,
        username=data.username,
        password=data.password,
    )

    return LoginResponse(
        user_id=user.user_id,
        access_token=user.access_token,
        refresh_token=user.refresh_token
    )


# @router.post("/refresh", response_model=TokenPair)
# async def refresh(body: RefreshRequest, db: db_dependency):
#     return await refresh_tokens(db, body.refresh_token)


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
