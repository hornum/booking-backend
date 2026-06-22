class BookingError(Exception):
    pass


class SlotTaken(BookingError):
    pass


class BookingNotFound(BookingError):
    pass


class InvalidBookingTime(BookingError):
    pass
