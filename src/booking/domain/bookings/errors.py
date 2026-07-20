class BookingError(Exception):
    pass


class SlotTaken(BookingError):
    pass


class BookingNotFound(BookingError):
    pass


class BookingAccessDenied(BookingError):
    pass


class InvalidBookingTime(BookingError):
    pass


class InvalidBookingStatusTransition(BookingError):
    pass


class BookingNotPayable(BookingError):
    pass
