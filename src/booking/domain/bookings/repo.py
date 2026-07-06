from datetime import datetime
from typing import Protocol

from booking.domain.bookings.models import Booking


class BookingRepository(Protocol):
    async def add(self, booking: Booking) -> Booking: ...

    async def get(self, booking_id: int) -> Booking | None: ...

    async def find_overlapping(
        self, room_id: int, start: datetime, end: datetime
    ) -> list[Booking]: ...

    async def update(self, booking: Booking) -> Booking: ...
