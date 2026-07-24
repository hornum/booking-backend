from dataclasses import dataclass


@dataclass(frozen=True)
class BookingFilter:
    user_id: int | None = None
