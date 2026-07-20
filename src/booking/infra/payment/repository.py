from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.payment.models import Payment
from booking.infra.payment.orm import PaymentORM


class SqlPaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(row: PaymentORM) -> Payment:
        return Payment(
            id=row.id,
            booking_id=row.booking_id,
            amount=row.amount,
            provider_session_id=row.provider_session_id,
            status=row.status,
        )

    @staticmethod
    def _to_orm(payment: Payment) -> PaymentORM:
        orm = PaymentORM(
            id=payment.id,
            booking_id=payment.booking_id,
            amount=payment.amount,
            provider_session_id=payment.provider_session_id,
            status=payment.status,
        )
        if payment.id is not None:
            orm.id = payment.id
        return orm

    async def add(self, payment: Payment) -> Payment:
        orm_payment = self._to_orm(payment)
        self._session.add(orm_payment)
        await self._session.flush()
        return self._to_domain(orm_payment)


    async def get(self, payment_id: int) -> Payment | None:
        orm_payment = await self._session.get(PaymentORM, payment_id)
        if orm_payment is None:
            return None

        return self._to_domain(orm_payment)

    async def get_by_session_id(self, session_id: str) -> Payment | None:
        query = select(PaymentORM).where(PaymentORM.provider_session_id == session_id)
        result = await self._session.execute(query)
        payment = result.scalar_one_or_none()
        if payment is None:
            return None
        return self._to_domain(payment)

    async def update(self, payment: Payment) -> Payment:
        orm = self._to_orm(payment)
        merged = await self._session.merge(orm)
        await self._session.flush()
        return self._to_domain(merged)
