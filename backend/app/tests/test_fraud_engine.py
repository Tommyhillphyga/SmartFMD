from datetime import UTC, datetime

import pytest

from app.services.fraud_engine import FraudEngine


@pytest.mark.anyio
async def test_low_pulses_per_liter_rule(session):
    engine = FraudEngine()
    alerts = await engine.evaluate_transaction(
        session=session,
        station_id="STA001",
        pump_id="PUMP01",
        device_id="DEV001",
        payload={
            "liters": 10,
            "pulse_count": 450,
            "duration_seconds": 60,
        },
    )
    assert any(alert.rule_name == "abnormally_low_pulses_per_liter" for alert in alerts)


@pytest.mark.anyio
async def test_meter_reset_rule(session):
    engine = FraudEngine()
    alerts = await engine.evaluate_telemetry(
        session=session,
        station_id="STA001",
        pump_id="PUMP01",
        device_id="DEV001",
        payload={
            "pulse_count": 100,
            "flowing": False,
            "timestamp": datetime.now(UTC),
        },
        previous_state={"pulse_count": 300, "stall_count": 0},
    )
    assert any(alert.rule_name == "sudden_meter_reset" for alert in alerts)

