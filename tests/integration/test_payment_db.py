from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.payment.models import Payment, PaymentStatus
from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.payment.repository import SqlPaymentRepository


async def test_add_and_get_success(session, booking_in_db):
    payment_repo = SqlPaymentRepository(session)
    payment = await payment_repo.add(Payment(
        booking_id=booking_in_db.id, amount=50000,
        provider_session_id="fake_sess_abc", status=PaymentStatus.PENDING,
    ))

    assert payment.id is not None

    fetched = await payment_repo.get(payment.id)
    assert fetched is not None
    assert fetched.amount == 50000
    assert fetched.booking_id == booking_in_db.id
    assert fetched.status == PaymentStatus.PENDING
    assert fetched.provider_session_id == "fake_sess_abc"


async def test_get_by_session_id_success(session, booking_in_db):
    payment_repo = SqlPaymentRepository(session)
    payment = await payment_repo.add(Payment(
        booking_id=booking_in_db.id, amount=50000,
        provider_session_id="fake_sess_abcde", status=PaymentStatus.PENDING,
    ))

    assert payment.id is not None

    fetched = await payment_repo.get_by_session_id("fake_sess_abcde")
    assert fetched is not None
    assert fetched.amount == 50000
    assert fetched.booking_id == booking_in_db.id


async def test_get_by_session_id_missing_returns_none(session):
    payment_repo = SqlPaymentRepository(session)
    assert await payment_repo.get_by_session_id("nonexistent") is None


async def test_update_persists_status(session, booking_in_db):
    payment_repo = SqlPaymentRepository(session)
    payment = await payment_repo.add(Payment(
        booking_id=booking_in_db.id, amount=50000,
        provider_session_id="fake_sess_abcde", status=PaymentStatus.PENDING,
    ))

    payment.change_status(PaymentStatus.SUCCEEDED)
    await payment_repo.update(payment)

    fetched = await payment_repo.get(payment.id)
    assert fetched.status == PaymentStatus.SUCCEEDED


async def test_payment_requires_existing_booking(session):
    payment_repo = SqlPaymentRepository(session)
    with pytest.raises(IntegrityError):
        await payment_repo.add(Payment(
            booking_id=99999, amount=50000,
            provider_session_id="x", status=PaymentStatus.PENDING,
        ))


async def test_session_id_is_unique(session, booking_in_db):
    payment_repo = SqlPaymentRepository(session)
    await payment_repo.add(Payment(
        booking_id=booking_in_db.id, amount=50000,
        provider_session_id="sessionid", status=PaymentStatus.PENDING,
    ))
    with pytest.raises(IntegrityError):
        await payment_repo.add(Payment(
            booking_id=booking_in_db.id, amount=50000,
            provider_session_id="sessionid", status=PaymentStatus.PENDING,
        ))

