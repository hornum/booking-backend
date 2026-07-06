import uuid

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer


def run_migrations(connection: Connection) -> None:
    alembic_config = AlembicConfig("alembic.ini")
    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17", driver="asyncpg") as container:
        yield container


@pytest_asyncio.fixture(scope="session")
async def template_engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url, poolclass=NullPool)
    async with engine.connect() as conn:
        await conn.run_sync(run_migrations)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_url(template_engine):
    admin_engine = create_async_engine(
        template_engine.url.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
    )
    db_name = f"test_{uuid.uuid4().hex}"
    template_name = template_engine.url.database

    async with admin_engine.connect() as conn:
        await conn.execute(
            text(f'CREATE DATABASE "{db_name}" TEMPLATE "{template_name}"')
        )

    yield template_engine.url.set(database=db_name)

    async with admin_engine.connect() as conn:
        await conn.execute(text(f'DROP DATABASE "{db_name}"'))
    await admin_engine.dispose()


@pytest_asyncio.fixture
async def session(test_db_url):
    engine = create_async_engine(test_db_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    await engine.dispose()


@pytest.fixture
def auth_json_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
    }
