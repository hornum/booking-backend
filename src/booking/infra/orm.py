from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from booking.domain.models import BookingStatus


class Base(DeclarativeBase):
    pass


class BookingORM(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int]
    start: Mapped[datetime]
    end: Mapped[datetime]
    status: Mapped[BookingStatus] = mapped_column(String(16))
