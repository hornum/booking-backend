from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session, verify_user_admin
from booking.api.schemas.booking import BookingResponse
from booking.api.schemas.common import PaginationParams
from booking.api.schemas.users import AdminUserResponse
from booking.domain.bookings.models import Booking
from booking.domain.users.errors import UserNotFound
from booking.domain.users.models import User
from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.booking import admin_get_bookings
from booking.service.user import (
    admin_change_user_status,
    admin_get_user,
    admin_get_users,
)

router = APIRouter(prefix="/admin/users", tags=["Admin users"])


@router.get("/{user_id}/", status_code=200, response_model=AdminUserResponse)
async def get_user_by_id(
    user_id: int,
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    repo = SqlUserRepository(session)
    try:
        user = await admin_get_user(repo=repo, target_user_id=user_id)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found") from None

    return user


@router.post("/{user_id}/status", status_code=200, response_model=AdminUserResponse)
async def change_user_is_active(
    target_user_id: int,
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
    new_active_status: bool = False,
) -> User:
    user_repo = SqlUserRepository(session)
    booking_repo = SqlBookingRepository(session)
    try:
        user = await admin_change_user_status(
            user_repo=user_repo,
            booking_repo=booking_repo,
            new_status=new_active_status,
            target_user_id=target_user_id,
        )
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found") from None

    return user


@router.get(
    path="/{user_id}/bookings", status_code=200, response_model=list[BookingResponse]
)
async def get_users_bookings(
    curr_user: Annotated[User, Depends(verify_user_admin)],
    user_id: int,
    query: Annotated[PaginationParams, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[Booking]:
    user_repo = SqlUserRepository(session)
    bookings_repo = SqlBookingRepository(session)
    return await admin_get_bookings(
        booking_repo=bookings_repo,
        user_repo=user_repo,
        offset=query.offset,
        limit=query.limit,
        target_user_id=user_id,
    )


@router.get("/", status_code=200, response_model=list[AdminUserResponse])
async def get_users(
    curr_user: Annotated[User, Depends(verify_user_admin)],
    query: Annotated[PaginationParams, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[User]:
    repo = SqlUserRepository(session)
    return await admin_get_users(repo=repo, offset=query.offset, limit=query.limit)
