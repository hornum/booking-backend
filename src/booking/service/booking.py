from datetime import datetime

from booking.domain.bookings.errors import (
    BookingAccessDenied,
    BookingNotFound,
    SlotTaken,
)
from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.bookings.repo import BookingRepository


async def _get_owned_booking(
    repo: BookingRepository, actor_id: int, booking_id: int
) -> Booking:
    booking = await repo.get(booking_id)
    if booking is None:
        raise BookingNotFound()
    if actor_id != booking.user_id:
        raise BookingAccessDenied()
    return booking


async def book_room(
    repo: BookingRepository, user_id: int, room_id: int, start: datetime, end: datetime
) -> Booking:
    overlapping = await repo.find_overlapping(room_id, start, end)
    if overlapping:
        raise SlotTaken()

    booking = Booking(
        room_id=room_id,
        user_id=user_id,
        start=start,
        end=end,
        status=BookingStatus.HOLD,
    )

    return await repo.add(booking)


async def confirm_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    booking.change_status(BookingStatus.CONFIRMED)
    return await repo.update(booking)


async def cancel_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    booking.change_status(BookingStatus.CANCELLED)
    return await repo.update(booking)


async def get_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    return booking
