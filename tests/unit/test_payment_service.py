import pytest

from booking.domain.bookings.errors import (
    BookingAccessDenied,
    BookingNotFound,
    BookingNotPayable,
)
from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.payment.models import PaymentStatus
from booking.infra.payment.fake_provider import FakePaymentProvider
from booking.service.payment import start_payment
from tests.fakes import FakeBookingRepository, FakePaymentRepository


async def test_start_payment_success(base_booking_model_data: dict):
    booking_repo = FakeBookingRepository()
    payment_repo = FakePaymentRepository()
    provider = FakePaymentProvider()

    await booking_repo.add(Booking(**base_booking_model_data))

    session = await start_payment(
        booking_repo=booking_repo,
        payment_repo=payment_repo,
        provider=provider,
        booking_id=1,
        actor_id=1,
    )
    assert len(provider.created_sessions) == 1
    amount, _ = provider.created_sessions[0]
    assert amount == 50000

    payment = await payment_repo.get_by_session_id(session.session_id)
    assert payment is not None
    assert payment.status == PaymentStatus.PENDING
    assert payment.booking_id == 1
    assert payment.amount == 50000


async def test_start_payment_access_denied(base_booking_model_data: dict):
    booking_repo = FakeBookingRepository()
    payment_repo = FakePaymentRepository()
    provider = FakePaymentProvider()

    await booking_repo.add(Booking(**base_booking_model_data))

    with pytest.raises(BookingAccessDenied):
        await start_payment(
            booking_repo=booking_repo,
            payment_repo=payment_repo,
            provider=provider,
            booking_id=1,
            actor_id=999,
        )


async def test_confirmed_booking_payment_fail(base_booking_model_data: dict):
    booking_repo = FakeBookingRepository()
    payment_repo = FakePaymentRepository()
    provider = FakePaymentProvider()

    confirmed_booking_data = {
        **base_booking_model_data,
        "status": BookingStatus.CONFIRMED,
    }
    await booking_repo.add(Booking(**confirmed_booking_data))

    with pytest.raises(BookingNotPayable):
        await start_payment(
            booking_repo=booking_repo,
            payment_repo=payment_repo,
            provider=provider,
            booking_id=1,
            actor_id=1,
        )


async def test_booking_not_found_payment_fail():
    booking_repo = FakeBookingRepository()
    payment_repo = FakePaymentRepository()
    provider = FakePaymentProvider()

    with pytest.raises(BookingNotFound):
        await start_payment(
            booking_repo=booking_repo,
            payment_repo=payment_repo,
            provider=provider,
            booking_id=1,
            actor_id=1,
        )
