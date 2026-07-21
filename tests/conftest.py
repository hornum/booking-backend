import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config as AlembicConfig
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from booking.api.dependencies import get_current_user, get_session
from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.payment.models import PaymentStatus
from booking.domain.refresh_token.models import RefreshToken
from booking.domain.users.models import User
from booking.infra import a_security
from booking.infra.a_security import hash_token
from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.payment.webhook_signature import create_webhook_signature
from booking.infra.token.repository import SqlTokenRepository
from booking.infra.users.repository import SqlUserRepository
from booking.main import app
from tests.fakes import FakeTokenRepository, FakeUserRepository

fast_pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=4)


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch):
    monkeypatch.setattr(a_security, "pwd_context", fast_pwd_context)


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


@pytest_asyncio.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(as_user):
    return as_user(1)


@pytest_asyncio.fixture
async def as_user(client):
    def _as_user(user_id: int):
        def override_get_current_user():
            return User(
                id=user_id,
                username=f"tester{user_id}",
                email=f"t{user_id}@t.com",
                hashed_password="x",
            )

        app.dependency_overrides[get_current_user] = override_get_current_user
        return client

    return _as_user


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def token_repo():
    return FakeTokenRepository()


@pytest.fixture
def api_booking_data():
    return {"room_id": 1, "start": "2026-06-01T10:00:00", "end": "2026-06-01T11:00:00"}


@pytest.fixture
def auth_json_data():
    return {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
    }


@pytest_asyncio.fixture
async def refresh_token_json_data(client, auth_json_data):
    tokens = await client.post(
        "/v1/auth/register",
        json=auth_json_data,
    )
    data = tokens.json()
    return {
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture
def base_booking_model_data():
    return {
        "room_id": 1,
        "user_id": 1,
        "start": datetime(2026, 1, 1, 10, 00, tzinfo=UTC),
        "end": datetime(2026, 1, 1, 12, 30, tzinfo=UTC),
        "status": BookingStatus.HOLD,
    }


@pytest.fixture
def base_payment_data():
    return {
        "booking_id": 1,
        "amount": 500,
        "provider_session_id": "x",
        "status": PaymentStatus.PENDING,
    }


@pytest_asyncio.fixture
async def booking_in_db(session):
    repo = SqlBookingRepository(session)
    return await repo.add(
        Booking(
            room_id=1,
            user_id=1,
            start=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            end=datetime(2026, 1, 1, 11, 0, tzinfo=UTC),
            status=BookingStatus.HOLD,
        )
    )


@pytest.fixture
def webhook_secret(monkeypatch: pytest.MonkeyPatch):
    secret = "very_fake_very_secret"
    monkeypatch.setattr(
        "booking.api.routes.payment.settings.PAYMENT_WEBHOOK_SECRET",
        secret,
    )
    return secret


@dataclass
class SignatureData:
    secret: str
    timestamp: int
    body: bytes
    signature: str


@pytest.fixture
def webhook_signature_data():
    secret = "secret"
    timestamp = 1000
    body = b"body"

    signature = create_webhook_signature(
        body=body,
        timestamp=timestamp,
        secret=secret,
    )

    return SignatureData(
        secret=secret,
        timestamp=timestamp,
        body=body,
        signature=signature,
    )


@dataclass(frozen=True)
class PaymentContext:
    booking_id: int
    session_id: str


@pytest_asyncio.fixture
async def pending_payment(
    auth_client,
    api_booking_data,
):
    booking_response = await auth_client.post(
        "/v1/bookings/1/book",
        json=api_booking_data,
    )
    assert booking_response.status_code == 201

    booking = booking_response.json()
    assert booking["status"] == "hold"

    payment_response = await auth_client.post(
        f"/v1/bookings/{booking['id']}/pay",
    )
    assert payment_response.status_code == 200

    payment = payment_response.json()
    session_id = payment["url"].split("/")[-1]

    return PaymentContext(
        booking_id=booking["id"],
        session_id=session_id,
    )


@dataclass(frozen=True)
class RefreshTokenFamily:
    first: str
    second: str


@pytest_asyncio.fixture
async def active_refresh_token_family(
    session,
):
    token_repo = SqlTokenRepository(session)
    user_repo = SqlUserRepository(session)
    user = await user_repo.add(
        User(
            username="testuser",
            email="testuser@test.test",
            hashed_password="123",
        )
    )
    first_token_str = "test_token"
    second_token_str = "test_token2"
    await token_repo.add(
        RefreshToken(
            token_hash=hash_token(first_token_str),
            user_id=user.id,
            expires_at=datetime(year=2030, month=1, day=1, tzinfo=UTC),
            created_at=datetime.now(UTC),
        )
    )
    await token_repo.add(
        RefreshToken(
            token_hash=hash_token(second_token_str),
            user_id=user.id,
            expires_at=datetime(year=2030, month=1, day=1, tzinfo=UTC),
            created_at=datetime.now(UTC),
        )
    )
    await session.commit()

    return RefreshTokenFamily(
        first=first_token_str,
        second=second_token_str,
    )
