from dataclasses import dataclass
from typing import Protocol


@dataclass
class PaymentSession:
    session_id: str
    payment_url: str


class PaymentProvider(Protocol):
    async def create_session(self, amount: int, booking_id: int) -> PaymentSession: ...
