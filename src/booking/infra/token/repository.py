from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.refresh_token.models import RefreshToken
from booking.infra.token.orm import RefreshTokenOrm


class SqlTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(row: RefreshTokenOrm) -> RefreshToken:
        return RefreshToken(
            id=row.id,
            token_hash=row.token_hash,
            user_id=row.user_id,
            expires_at=row.expires_at,
            created_at=row.created_at,
            revoked_at=row.revoked_at,
        )

    @staticmethod
    def _to_orm(token: RefreshToken) -> RefreshTokenOrm:
        orm = RefreshTokenOrm(
            token_hash=token.token_hash,
            user_id=token.user_id,
            expires_at=token.expires_at,
            revoked_at=token.revoked_at,
        )
        if token.id is not None:
            orm.id = token.id
        return orm

    async def add(self, token: RefreshToken) -> RefreshToken:
        orm_token = self._to_orm(token)
        self._session.add(orm_token)
        await self._session.flush()
        return self._to_domain(orm_token)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(RefreshTokenOrm).where(RefreshTokenOrm.token_hash == token_hash)
        result = await self._session.execute(query)
        token = result.scalar_one_or_none()
        if token is None:
            return None
        return self._to_domain(token)

    async def revoke(self, token: RefreshToken) -> None:
        await self._session.execute(
            update(RefreshTokenOrm)
            .where(RefreshTokenOrm.id == token.id)
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self._session.flush()

    async def revoke_all(self, user_id: int) -> None: ...
