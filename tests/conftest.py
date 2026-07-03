import pytest_asyncio
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from booking.infra.db import Base
from booking.infra.bookings.orm import BookingORM
from config.config import settings


@pytest_asyncio.fixture(scope="session")
async def engine():
    test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
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


@pytest.fixture
def auth_json_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
    }
