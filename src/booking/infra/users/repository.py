from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.users.models import User, UserRole
from booking.infra.users.orm import UserORM


class SqlUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(row: UserORM) -> User:
        return User(
            id=row.id,
            role=UserRole(row.role),
            created_at=row.created_at,
            email=row.email,
            username=row.username,
            hashed_password=row.hashed_password,
        )

    @staticmethod
    def _to_orm(user: User) -> UserORM:
        orm = UserORM(
            id=user.id,
            role=user.role,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
        )
        if user.id is not None:
            orm.id = user.id
        return orm

    async def add(self, user: User) -> User:
        orm_user = self._to_orm(user)
        self._session.add(orm_user)
        await self._session.flush()
        return self._to_domain(orm_user)

    async def get(self, user_id: int) -> User | None:
        orm_user = await self._session.get(UserORM, user_id)

        return self._to_domain(orm_user) if orm_user is not None else None

    async def find_by_username(self, username: str) -> User | None:
        query = select(UserORM).where(UserORM.username == username)
        result = await self._session.execute(query)
        orm_user = result.scalar_one_or_none()

        return self._to_domain(orm_user) if orm_user is not None else None

    async def find_existing(self, email: str, username: str) -> User | None:
        query = select(UserORM).where(
            or_(UserORM.username == username, UserORM.email == email)
        )
        result = await self._session.execute(query)
        orm_user = result.scalar_one_or_none()

        return self._to_domain(orm_user) if orm_user is not None else None
