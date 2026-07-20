import pytest

from booking.domain.payment.errors import (
    InvalidPaymentAmount,
    InvalidPaymentStatusTransition,
)
from booking.domain.payment.models import Payment, PaymentStatus


def test_amount_0_or_less_error():
    with pytest.raises(InvalidPaymentAmount):
        Payment(
            booking_id=1,
            amount=0,
            provider_session_id="123",
            status=PaymentStatus.PENDING,
            id=1,
        )


def test_pending_can_be_succeed(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.SUCCEEDED)
    assert payment.status == PaymentStatus.SUCCEEDED


def test_pending_can_be_failed(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.FAILED)
    assert payment.status == PaymentStatus.FAILED


def test_pending_can_be_expired(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.EXPIRED)
    assert payment.status == PaymentStatus.EXPIRED


def test_succeed_cant_be_failed(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.SUCCEEDED)
    with pytest.raises(InvalidPaymentStatusTransition):
        payment.change_status(PaymentStatus.FAILED)


def test_succeed_cant_be_expired(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.SUCCEEDED)
    with pytest.raises(InvalidPaymentStatusTransition):
        payment.change_status(PaymentStatus.EXPIRED)


def test_expired_cant_be_succeed(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.EXPIRED)
    with pytest.raises(InvalidPaymentStatusTransition):
        payment.change_status(PaymentStatus.SUCCEEDED)


def test_failed_cant_be_succeed(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    payment.change_status(PaymentStatus.FAILED)
    with pytest.raises(InvalidPaymentStatusTransition):
        payment.change_status(PaymentStatus.SUCCEEDED)


def test_direct_status_assignment_forbidden(base_payment_data: dict):
    payment = Payment(**base_payment_data)
    with pytest.raises(AttributeError):
        payment.status = PaymentStatus.SUCCEEDED
