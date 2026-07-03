from datetime import datetime

from booking.infra.bookings.repository import SqlBookingRepository
from booking.service.booking import book_room


async def test_book_room_persists_to_db(session):
    repo = SqlBookingRepository(session)

    booking = await book_room(
        repo=repo, user_id=1, room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    assert booking.id is not None

    fetched = await repo.get(booking.id)
    assert fetched is not None
    assert fetched.room_id == 1
