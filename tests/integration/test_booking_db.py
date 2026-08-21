from datetime import datetime, timezone

import pytest
from asyncpg.pgproto.pgproto import timedelta

from booking.domain.bookings.errors import SlotTaken
from booking.domain.bookings.models import Booking, BookingStatus
from booking.service.booking import book_room


async def test_db_prevents_race_condition(booking_repo, base_booking_model_data):
    booking_1 = Booking(**base_booking_model_data)
    await booking_repo.add(booking_1)

    booking_2 = Booking(**base_booking_model_data)
    with pytest.raises(SlotTaken):
        await booking_repo.add(booking_2)


async def test_diff_bookings_ends_and_starts_same_time(
        booking_repo, base_booking_model_data
):
    now = datetime.now(timezone.utc)
    booking_1 = Booking(
        **{
            **base_booking_model_data,
            "start": now,
            "end": now + timedelta(hours=1)
        }
    )
    await booking_repo.add(booking_1)

    booking_2 = await booking_repo.add(Booking(
        **{
            **base_booking_model_data,
            "start": now + timedelta(hours=1),
            "end": now + timedelta(hours=2)
        }
    ))
    assert booking_2.status == BookingStatus.HOLD


async def test_book_room_persists_to_db(booking_repo):
    booking = await book_room(
        repo=booking_repo,
        user_id=1,
        room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    assert booking.id is not None

    fetched = await booking_repo.get(booking.id)
    assert fetched is not None
    assert fetched.room_id == 1

