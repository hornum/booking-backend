import pytest
from datetime import datetime

from booking.service.booking import book_room
from booking.infra.repository import SqlBookingRepository
from booking.domain.errors import SlotTaken


async def test_book_room_persists_to_db(session):
    repo = SqlBookingRepository(session)

    booking = await book_room(
        repo=repo, user_id=1, room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    # бронь сохранилась и получила настоящий id из базы
    assert booking.id is not None

    # достаём её обратно из базы — она там
    fetched = await repo.get(booking.id)
    assert fetched is not None
    assert fetched.room_id == 1
