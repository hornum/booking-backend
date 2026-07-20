from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from booking.domain.payment.models import PaymentStatus
from booking.infra.db import Base


class PaymentORM(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_session_id: Mapped[str] = mapped_column(index=True, unique=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    amount: Mapped[int] = mapped_column()
    status: Mapped[PaymentStatus] = mapped_column(String(16))
