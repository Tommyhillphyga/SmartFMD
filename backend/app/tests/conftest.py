import os
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./smartfmd-test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MQTT_ENABLED", "false")
os.environ.setdefault("APP_AUTO_CREATE_SCHEMA", "false")

from app.db.base import Base
from app.db.session import get_db_session, get_redis
from app.main import app
from app.models import Company, Device, Nozzle, Pump, Station, User
from app.core.enums import DeviceStatus, PumpStatus, Role
from app.core.security import hash_password
from app.services.runtime import telemetry_service


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return None


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def engine():
    db_engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield db_engine
    await db_engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db_session:
        for table in reversed(Base.metadata.sorted_tables):
            await db_session.execute(table.delete())
        await db_session.commit()

        company = Company(id="COMTST", name="Test Company")
        station = Station(
            id="STA001",
            company_id=company.id,
            name="Test Station",
            location="Lagos Island",
            city="Lagos",
        )
        pump = Pump(
            id="PUMP01",
            station_id=station.id,
            name="Pump 01",
            status=PumpStatus.IDLE,
        )
        nozzle = Nozzle(id="NOZ01", pump_id=pump.id, label="A", price_per_liter=972)
        device = Device(
            id="DEV001",
            station_id=station.id,
            pump_id=pump.id,
            firmware_version="1.0.0",
            status=DeviceStatus.ONLINE,
        )
        admin = User(
            id="USRADMIN",
            company_id=company.id,
            full_name="Admin User",
            email="admin@example.com",
            hashed_password=hash_password("Admin123!"),
            role=Role.SUPER_ADMIN,
        )
        attendant = User(
            id="ATT001",
            company_id=company.id,
            station_id=station.id,
            full_name="Attendant User",
            email="attendant@example.com",
            hashed_password=hash_password("Password123!"),
            role=Role.ATTENDANT,
        )
        db_session.add_all([company, station, pump, nozzle, device, admin, attendant])
        await db_session.commit()
        yield db_session


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest_asyncio.fixture(autouse=True)
async def override_dependencies(session, fake_redis, monkeypatch) -> AsyncGenerator[None, None]:
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    async def _get_redis() -> AsyncGenerator[FakeRedis, None]:
        yield fake_redis

    app.dependency_overrides[get_db_session] = _get_db
    app.dependency_overrides[get_redis] = _get_redis
    monkeypatch.setattr("app.services.telemetry.queue_alert_notifications", lambda alert: None)
    monkeypatch.setattr("app.services.notifications.queue_alert_notifications", lambda alert: None)
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def access_token(async_client: AsyncClient) -> str:
    response = await async_client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def telemetry_payload() -> dict:
    return {
        "device_id": "DEV001",
        "pump_id": "PUMP01",
        "pulse_count": 120,
        "flowing": True,
        "voltage": 12.1,
        "rssi": -70,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def transaction_payload() -> dict:
    return {
        "pump_id": "PUMP01",
        "liters": 12.35,
        "amount": 12000,
        "price_per_liter": 972,
        "pulse_count": 1235,
        "duration_seconds": 55,
        "attendant_id": "ATT001",
        "timestamp": (datetime.now(UTC) + timedelta(seconds=1)).isoformat(),
    }


@pytest.fixture
def ingestion_service():
    return telemetry_service
