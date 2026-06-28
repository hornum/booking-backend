from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from booking.infra.orm import Base

DATABASE_URL = "postgresql+asyncpg://booking:booking@localhost:5432/booking"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
