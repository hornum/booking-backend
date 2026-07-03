from datetime import datetime, timezone

from booking.domain.bookings.models import Booking
from booking.domain.refresh_token.models import RefreshToken
from booking.domain.users.models import User


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
            if b.room_id == room_id and b.start < end and start < b.end:
                bookings.append(b)

        return bookings


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: list[User] = []
        self._next_id = 1

    async def add(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self._users.append(user)
        return user

    async def get(self, user_id: int) -> User | None:
        for user in self._users:
            if user.id == user_id:
                return user

        return None

    async def find_by_username(self, username: str) -> User | None:
        for user in self._users:
            if user.username == username:
                return user
        return None

    async def find_existing(self, email: str, username: str) -> User | None:
        for user in self._users:
            if user.email == email and user.username == username:
                return user

        return None


class FakeTokenRepository:
    def __init__(self) -> None:
        self._tokens: list[RefreshToken] = []
        self._next_id = 1

    async def add(self, token: RefreshToken) -> RefreshToken:
        token.id = self._next_id
        self._next_id += 1
        self._tokens.append(token)
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        for token in self._tokens:
            if token.token_hash == token_hash:
                return token

        return None

    async def revoke(self, token: RefreshToken) -> None:
        for stored in self._tokens:
            if stored.id == token.id:
                stored.revoked_at = datetime.now(timezone.utc)
                return

    async def revoke_all(self, token: RefreshToken) -> None: ...
