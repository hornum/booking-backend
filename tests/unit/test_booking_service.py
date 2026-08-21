import pytest

from booking.domain.bookings.errors import (
    BookingAccessDenied,
    BookingNotFound,
    InvalidBookingStatusTransition,
)
from booking.domain.bookings.models import Booking, BookingStatus
from booking.service.booking import cancel_booking, confirm_booking, get_booking


async def test_confirm_booking_sets_confirmed(
    base_booking_model_data: dict,
        fake_booking_repo,
):
    booking = await fake_booking_repo.add(Booking(**base_booking_model_data))
    result = await confirm_booking(fake_booking_repo, booking.id, 1)
    assert result.status == BookingStatus.CONFIRMED


async def test_confirm_missing_booking_raises(fake_booking_repo):
    with pytest.raises(BookingNotFound):
        await confirm_booking(fake_booking_repo, 999, 1)


async def test_confirm_canceled_booking_raises(
    base_booking_model_data: dict,
        fake_booking_repo,
):
    booking = await fake_booking_repo.add(Booking(**base_booking_model_data))
    await cancel_booking(fake_booking_repo, booking.id, 1)
    with pytest.raises(InvalidBookingStatusTransition):
        await confirm_booking(fake_booking_repo, booking.id, 1)


async def test_booking_confirm_auth_fail(base_booking_model_data: dict,
                                         fake_booking_repo):
    booking = await fake_booking_repo.add(Booking(**base_booking_model_data))
    with pytest.raises(BookingAccessDenied):
        await confirm_booking(fake_booking_repo, booking.id, 999)


async def test_booking_cancel_auth_fail(base_booking_model_data: dict,
                                        fake_booking_repo):
    booking = await fake_booking_repo.add(Booking(**base_booking_model_data))
    with pytest.raises(BookingAccessDenied):
        await cancel_booking(fake_booking_repo, booking.id, 999)


async def test_booking_get_auth_fail(base_booking_model_data: dict, fake_booking_repo):
    booking = await fake_booking_repo.add(Booking(**base_booking_model_data))
    with pytest.raises(BookingAccessDenied):
        await get_booking(fake_booking_repo, booking.id, 999)
