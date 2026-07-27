from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session, verify_user_admin
from booking.api.schemas.booking import AdminCreateBookingRequest, BookingResponse
from booking.api.schemas.common import AdminBookingQueryParams
from booking.domain.bookings.errors import (
    BookingNotFound,
    InvalidBookingStatusTransition,
    SlotTaken,
)
from booking.domain.bookings.models import Booking
from booking.domain.users.errors import UserNotFound
from booking.domain.users.models import User
from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.booking import (
    admin_cancel_booking,
    admin_confirm_booking,
    admin_create_booking,
    admin_get_bookings,
)

router = APIRouter(prefix="/admin/bookings", tags=["Admin bookings"])


@router.post(
    path="/{booking_id}/confirm", response_model=BookingResponse, status_code=200
)
async def confirm_booking_endpoint(
    booking_id: int,
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")
    try:
        booking = await admin_confirm_booking(repo=repo, booking_id=booking_id)
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except InvalidBookingStatusTransition:
        raise HTTPException(
            status_code=409, detail="Invalid status transition"
        ) from None
    return booking


@router.post(
    path="/{booking_id}/cancel", response_model=BookingResponse, status_code=200
)
async def cancel_booking_endpoint(
    booking_id: int,
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")

    try:
        booking = await admin_cancel_booking(repo=repo, booking_id=booking_id)
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except InvalidBookingStatusTransition:
        raise HTTPException(
            status_code=409, detail="Invalid status transition"
        ) from None

    return booking


@router.post(
    path="/create_confirmed_booking", response_model=BookingResponse, status_code=200
)
async def create_booking(
    payload: AdminCreateBookingRequest,
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    booking_repo = SqlBookingRepository(session)
    user_repo = SqlUserRepository(session)

    try:
        booking = await admin_create_booking(
            user_repo=user_repo,
            booking_repo=booking_repo,
            target_user_id=payload.target_user_id,
            room_id=payload.room_id,
            start=payload.start,
            end=payload.end,
            create_confirmed=payload.create_confirmed,
        )
    except UserNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except SlotTaken:
        raise HTTPException(status_code=409, detail="Slot already taken") from None

    return booking


@router.get(path="/", response_model=list[BookingResponse], status_code=200)
async def get_bookings(
    curr_user: Annotated[User, Depends(verify_user_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
    query: Annotated[AdminBookingQueryParams, Query()],
) -> list[Booking]:
    bookings_repo = SqlBookingRepository(session)
    user_repo = SqlUserRepository(session)

    bookings = await admin_get_bookings(
        booking_repo=bookings_repo,
        user_repo=user_repo,
        target_user_id=query.target_user_id,
        offset=query.offset,
        limit=query.limit,
    )
    return bookings
