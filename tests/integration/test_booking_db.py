from datetime import datetime

from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.service.auth import register_user
from booking.service.booking import book_room


async def test_book_room_persists_to_db(session):
    repo = SqlBookingRepository(session)

    booking = await book_room(
        repo=repo,
        user_id=1,
        room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    assert booking.id is not None

    fetched = await repo.get(booking.id)
    assert fetched is not None
    assert fetched.room_id == 1


async def test_reg_success(session):
    user_repo = SqlUserRepository(session)
    token_repo = SqlTokenRepository(session)

    user = await register_user(
        user_repo=user_repo,
        token_repo=token_repo,
        username="testdummy",
        email="testdummy@testdummy.com",
        password="long_password",
    )

    assert user.access_token
    assert user.refresh_token
    assert user.user_id
