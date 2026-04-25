from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.anyio
async def test_websocket_receives_broadcast(session, fake_redis, ingestion_service):
    with TestClient(app) as client:
        with client.websocket_connect("/ws/dashboard/STA001") as websocket:
            await ingestion_service.process_telemetry(
                session=session,
                redis=fake_redis,
                station_id="STA001",
                payload={
                    "device_id": "DEV001",
                    "pump_id": "PUMP01",
                    "pulse_count": 100,
                    "flowing": True,
                    "voltage": 12.1,
                    "rssi": -65,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )
            message = websocket.receive_json()
            assert message["event"] == "telemetry"
            assert message["pump_id"] == "PUMP01"
