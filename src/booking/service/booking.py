from datetime import datetime

from booking.domain.bookings.errors import SlotTaken
from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.bookings.repo import BookingRepository


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
