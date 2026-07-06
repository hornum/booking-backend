from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.bookings.models import Booking
from booking.infra.bookings.orm import BookingORM


class SqlBookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(row: BookingORM) -> Booking:
        return Booking(
            id=row.id,
            room_id=row.room_id,
            user_id=row.user_id,
            start=row.start,
            end=row.end,
            status=row.status,
        )

    @staticmethod
    def _to_orm(booking: Booking) -> BookingORM:
        orm = BookingORM(
            room_id=booking.room_id,
            user_id=booking.user_id,
            start=booking.start,
            end=booking.end,
            status=booking.status,
        )
        if booking.id is not None:
            orm.id = booking.id
        return orm

    async def add(self, booking: Booking) -> Booking:
        orm_booking = self._to_orm(booking)
        self._session.add(orm_booking)
        await self._session.flush()
        return self._to_domain(orm_booking)

    async def get(self, booking_id: int) -> Booking | None:
        orm_booking = await self._session.get(BookingORM, booking_id)
        if orm_booking is None:
            return None

        return self._to_domain(orm_booking)

    async def find_overlapping(
        self, room_id: int, start: datetime, end: datetime
    ) -> list[Booking]:
        query = select(BookingORM).where(
            BookingORM.room_id == room_id,
            BookingORM.start < end,
            start < BookingORM.end,
        )
        result = await self._session.execute(query)
        rows = result.scalars().all()

        bookings = [self._to_domain(r) for r in rows]
        return bookings

    async def update(self, booking: Booking) -> Booking:
        orm = self._to_orm(booking)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return self._to_domain(merged)
