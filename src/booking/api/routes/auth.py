from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session
from booking.api.schemas.auth import (
    AuthResponse,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    UserRegister,
)
from booking.domain.refresh_token.errors import TokenExpired, TokenNotFound
from booking.domain.users.errors import UserAlreadyExists
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.auth import (
    ReuseDetected,
    login_user,
    refresh_tokens,
    register_user,
)

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/register")
async def register(
    data: UserRegister, session: Annotated[AsyncSession, Depends(get_session)]
) -> AuthResponse:
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
        raise HTTPException(status_code=409, detail="User already exists") from None

    return AuthResponse(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        user_id=user.user_id,
    )


@router.post("/login")
async def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
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
        refresh_token=user.refresh_token,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    body: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefreshResponse | Response:
    token_repo = SqlTokenRepository(session)

    try:
        result = await refresh_tokens(
            token_repo=token_repo, refresh_token=body.refresh_token
        )
    except (TokenExpired, TokenNotFound):
        raise HTTPException(status_code=401, detail="Invalid refresh token") from None

    if isinstance(result, ReuseDetected):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid refresh token"},
        )

    return RefreshResponse(
        refresh_token=result.refresh_token,
        access_token=result.access_token,
    )


# @router.post("/logout")
# async def logout(body: RefreshRequest, db: db_dependency):
#     await logout_user(db, body.refresh_token)
#     return {"message": "Successfully logged out"}
