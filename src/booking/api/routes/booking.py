from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session, get_current_user
from booking.api.schemas.booking import BookRoomRequest, BookingResponse
from booking.domain.bookings.errors import SlotTaken
from booking.domain.users.models import User
from booking.infra.bookings.repository import SqlBookingRepository
from booking.service.booking import book_room

router = APIRouter(prefix="/v1/rooms", tags=["booking"])


@router.post(
    path="/{room_id}/book",
    response_model=BookingResponse,
    status_code=201)
async def room_book_router(
        curr_user: Annotated[User, Depends(get_current_user)],
        room_id: int,
        payload: BookRoomRequest,
        session: AsyncSession = Depends(get_session),
):
    repo = SqlBookingRepository(session)
    try:
        booking = await book_room(
            repo=repo, user_id=curr_user.id, room_id=room_id, start=payload.start, end=payload.end
        )
    except SlotTaken:
        raise HTTPException(status_code=409, detail="Slot already taken")

    return booking
