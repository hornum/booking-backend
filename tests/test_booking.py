from datetime import datetime

import pytest

from booking.domain.errors import SlotTaken, InvalidBookingTime
from booking.domain.models import Booking, BookingStatus
from booking.service.booking import book_room
from tests.fakes import FakeBookingRepository


@pytest.mark.asyncio
async def test_overlapping_error():
    repo = FakeBookingRepository()

    await book_room(
        repo=repo,
        user_id=1,
        room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(SlotTaken):
        await book_room(
            repo=repo,
            user_id=1,
            room_id=1,
            start=datetime(2026, 1, 1, 9, 30),
            end=datetime(2026, 1, 1, 10, 30),
        )


def test_start_after_end_error():
    with pytest.raises(InvalidBookingTime):
        Booking(
            room_id=1,
            user_id=1,
            start=datetime(2026, 1, 1, 9, 30),
            end=datetime(2026, 1, 1, 8, 30),
            status=BookingStatus.HOLD,
        )
