from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from booking.domain.bookings.errors import InvalidBookingTime


class BookingStatus(StrEnum):
    HOLD = "hold"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Booking:
    room_id: int
    user_id: int
    start: datetime
    end: datetime
    status: BookingStatus
    id: int | None = None

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise InvalidBookingTime()
