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


class Booking:
    def __init__(
            self,
            room_id: int,
            user_id: int,
            start: datetime,
            end: datetime,
            status: BookingStatus,
            id: int | None = None,):
        if start >= end:
            raise InvalidBookingTime()
        self.room_id=room_id
        self.user_id=user_id
        self.start=start
        self.end=end
        self._status=status
        self.id=id

    @property
    def status(self) -> BookingStatus:
        return self._status


    def change_status(self, new_status: BookingStatus) -> None:
        if new_status not in _ALLOWED_STATUS_TRANSITIONS[self._status]:
            raise InvalidStatusTransition()
        self._status = new_status
