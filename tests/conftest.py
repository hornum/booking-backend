import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from booking.infra.orm import Base, BookingORM

TEST_DATABASE_URL = "postgresql+asyncpg://booking:booking@localhost:5433/booking"


@pytest_asyncio.fixture(scope="session")
async def engine():
    test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
        await db_session.rollback()
    async with factory() as cleanup:
        await cleanup.execute(delete(BookingORM))
        await cleanup.commit()
