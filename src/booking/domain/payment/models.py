from datetime import UTC, datetime
from enum import StrEnum

from booking.domain.payment.errors import (
    InvalidPaymentAmount,
    InvalidPaymentStatusTransition,
)


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"


_ALLOWED_PAYMENT_STATUS_TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
    PaymentStatus.PENDING: {
        PaymentStatus.SUCCEEDED,
        PaymentStatus.FAILED,
        PaymentStatus.EXPIRED,
    },
    PaymentStatus.SUCCEEDED: set(),
    PaymentStatus.FAILED: set(),
    PaymentStatus.EXPIRED: set(),
}


class Payment:
    def __init__(
        self,
        booking_id: int,
        amount: int,
        provider_session_id: str,
        status: PaymentStatus,
        created_at: datetime | None = None,
        id: int | None = None,
    ):
        if amount <= 0:
            raise InvalidPaymentAmount()

        self.booking_id = booking_id
        self.created_at = (created_at or datetime.now(UTC),)
        self.amount = amount
        self.provider_session_id = provider_session_id
        self._status = status
        self.id = id

    @property
    def status(self) -> PaymentStatus:
        return self._status

    def change_status(self, new_status: PaymentStatus) -> None:
        if new_status not in _ALLOWED_PAYMENT_STATUS_TRANSITIONS[self._status]:
            raise InvalidPaymentStatusTransition()
        self._status = new_status
