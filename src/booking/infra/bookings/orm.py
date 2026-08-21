from datetime import datetime

from sqlalchemy import DateTime, String, func, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from booking.domain.bookings.models import BookingStatus
from booking.infra.db import Base


class BookingORM(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    room_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int]
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[BookingStatus] = mapped_column(String(16))

    __table_args__ = (
        ExcludeConstraint(
            ("room_id", "="),
            (text("tstzrange(start, end, '[)')"), "&&"),
            name="booking_no_overlap",
            where=text("status IN ('hold', 'confirmed')"),
        ),
    )
