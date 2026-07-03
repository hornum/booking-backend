from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.config import settings

engine = create_async_engine(settings.database_url)

class Base(DeclarativeBase):
    pass

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
