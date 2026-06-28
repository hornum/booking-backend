from datetime import datetime

from booking.domain.models import Booking


class FakeBookingRepository:
    def __init__(self) -> None:
        self._bookings: list[Booking] = []
        self._next_id = 1

    async def add(self, booking: Booking) -> Booking:
        booking.id = self._next_id
        self._next_id += 1
        self._bookings.append(booking)
        return booking

    async def get(self, booking_id: int) -> Booking | None:
        for booking in self._bookings:
            if booking.id == booking_id:
                return booking

        return None

    async def find_overlapping(
        self, room_id: int, start: datetime, end: datetime
    ) -> list[Booking]:
        bookings = []
        for b in self._bookings:
            if b.room_id == room_id:
                if b.start < end and start < b.end:
                    bookings.append(b)

        return bookings
