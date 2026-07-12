import pytest

from booking.domain.bookings.errors import BookingNotFound, InvalidStatusTransition
from booking.domain.bookings.models import Booking, BookingStatus
from booking.service.booking import cancel_booking, confirm_booking
from tests.fakes import FakeBookingRepository


async def test_confirm_booking_sets_confirmed(base_booking_data: dict):
    repo = FakeBookingRepository()
    booking = await repo.add(Booking(**base_booking_data))
    result = await confirm_booking(repo, booking.id)
    assert result.status == BookingStatus.CONFIRMED


async def test_confirm_missing_booking_raises():
    repo = FakeBookingRepository()
    with pytest.raises(BookingNotFound):
        await confirm_booking(repo, 999)


async def test_confirm_canceled_booking_raises(base_booking_data: dict):
    repo = FakeBookingRepository()
    booking = await repo.add(Booking(**base_booking_data))
    await cancel_booking(repo, booking.id)
    with pytest.raises(InvalidStatusTransition):
        await confirm_booking(repo, booking.id)
