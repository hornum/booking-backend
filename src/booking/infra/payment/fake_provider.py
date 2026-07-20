import uuid

from booking.domain.payment.provider import PaymentSession


class FakePaymentProvider:
    def __init__(self) -> None:
        self.created_sessions: list[tuple[int, PaymentSession]] = []

    async def create_session(self, amount: int, booking_id: int) -> PaymentSession:
        session_id = f"fake_{uuid.uuid4().hex}"
        session = PaymentSession(
            session_id=session_id,
            payment_url=f"https://fake-pay.local/checkout/{session_id}",
        )
        self.created_sessions.append((amount, session))
        return session
