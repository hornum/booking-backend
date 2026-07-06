from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from booking.domain.bookings.errors import InvalidBookingTime, InvalidStatusTransition


class BookingStatus(StrEnum):
    HOLD = "hold"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


_ALLOWED_STATUS_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.HOLD: {
        BookingStatus.CONFIRMED, BookingStatus.CANCELLED, BookingStatus.EXPIRED
    },
    BookingStatus.CONFIRMED: {BookingStatus.CANCELLED},
    BookingStatus.CANCELLED: set(),
    BookingStatus.EXPIRED: set(),
}


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

    def change_status(self, new_status: BookingStatus) -> None:
        if new_status not in _ALLOWED_STATUS_TRANSITIONS[self.status]:
            raise InvalidStatusTransition()
        self.status = new_status

