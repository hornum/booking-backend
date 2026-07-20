from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_current_user, get_session
from booking.api.schemas.booking import BookingResponse, BookRoomRequest
from booking.domain.bookings.errors import (
    BookingAccessDenied,
    BookingNotFound,
    InvalidStatusTransition,
    SlotTaken,
)
from booking.domain.bookings.models import Booking
from booking.domain.users.models import User
from booking.infra.bookings.repository import SqlBookingRepository
from booking.service.booking import (
    book_room,
    cancel_booking,
    confirm_booking,
    get_booking,
)

router = APIRouter(prefix="/v1/bookings", tags=["booking"])


@router.post(path="/{room_id}/book", response_model=BookingResponse, status_code=201)
async def room_book_router(
    curr_user: Annotated[User, Depends(get_current_user)],
    room_id: int,
    payload: BookRoomRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")
    try:
        booking = await book_room(
            repo=repo,
            user_id=curr_user.id,
            room_id=room_id,
            start=payload.start,
            end=payload.end,
        )
    except SlotTaken:
        raise HTTPException(status_code=409, detail="Slot already taken") from None

    return booking


@router.get(path="/{booking_id}", response_model=BookingResponse)
async def booking_get_router(
    booking_id: int,
    curr_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")
    try:
        booking = await get_booking(
            repo=repo, booking_id=booking_id, actor_id=curr_user.id
        )
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except BookingAccessDenied:
        raise HTTPException(status_code=403, detail="Booking access denied") from None
    return booking


@router.post(
    path="/{booking_id}/confirm", response_model=BookingResponse, status_code=200
)
async def confirm_booking_endpoint(
    booking_id: int,
    curr_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")
    try:
        booking = await confirm_booking(
            repo=repo, booking_id=booking_id, actor_id=curr_user.id
        )
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except BookingAccessDenied:
        raise HTTPException(status_code=403, detail="Booking access denied") from None
    except InvalidStatusTransition:
        raise HTTPException(
            status_code=409, detail="Invalid status transition"
        ) from None
    return booking


@router.post(path="/{booking_id}/pay")
async def pay_for_booking_endpoint(
        booking_id: int,
        curr_user_id: Annotated[User, Depends(get_current_user_id)],
        session: Annotated[AsyncSession, Depends(get_session)],
        provider: Annotated[PaymentProvider, Depends(get_payment_provider)],
) -> PaymentUrlResponse:
    booking_repo = SqlBookingRepository(session)
    payment_repo = SqlPaymentRepository(session)

    try:
        payment = await start_payment(
            booking_repo=booking_repo,
            payment_repo=payment_repo,
            provider=provider,
            booking_id=booking_id,
            actor_id=curr_user_id,
        )
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except BookingAccessDenied:
        raise HTTPException(status_code=403, detail="Booking access denied") from None
    except BookingNotPayable:
        raise HTTPException(status_code=409, detail="Booking not payable") from None

    return PaymentUrlResponse(url=payment.payment_url)


@router.post(
    path="/{booking_id}/cancel", response_model=BookingResponse, status_code=200
)
async def cancel_booking_endpoint(
    booking_id: int,
    curr_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Booking:
    repo = SqlBookingRepository(session)
    if curr_user.id is None:
        raise RuntimeError("Authenticated user has no id")
    try:
        booking = await cancel_booking(
            repo=repo, booking_id=booking_id, actor_id=curr_user.id
        )
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found") from None
    except BookingAccessDenied:
        raise HTTPException(status_code=403, detail="Booking access denied") from None
    except InvalidStatusTransition:
        raise HTTPException(
            status_code=409, detail="Invalid status transition"
        ) from None
    return booking
