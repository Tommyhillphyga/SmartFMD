import pytest
from sqlalchemy import select

from app.models import TelemetryLog, Transaction


@pytest.mark.anyio
async def test_processes_telemetry_and_transaction(
    session,
    fake_redis,
    ingestion_service,
    telemetry_payload,
    transaction_payload,
):
    await ingestion_service.process_telemetry(
        session=session,
        redis=fake_redis,
        station_id="STA001",
        payload=telemetry_payload,
    )
    await ingestion_service.process_transaction(
        session=session,
        redis=fake_redis,
        station_id="STA001",
        payload=transaction_payload,
    )

    telemetry_logs = (await session.execute(select(TelemetryLog))).scalars().all()
    transactions = (await session.execute(select(Transaction))).scalars().all()
    assert len(telemetry_logs) == 1
    assert len(transactions) == 1

