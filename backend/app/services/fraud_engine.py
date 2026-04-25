from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertSeverity
from app.models import Device, Station, Transaction


EXPECTED_PULSES_PER_LITER = 100.0


@dataclass
class GeneratedAlert:
    station_id: str
    severity: AlertSeverity
    rule_name: str
    message: str
    pump_id: str | None = None
    device_id: str | None = None
    metadata_json: dict[str, Any] = field(default_factory=dict)


class FraudEngine:
    async def evaluate_telemetry(
        self,
        *,
        session: AsyncSession,
        station_id: str,
        pump_id: str,
        device_id: str,
        payload: dict[str, Any],
        previous_state: dict[str, Any] | None,
    ) -> list[GeneratedAlert]:
        alerts: list[GeneratedAlert] = []
        pulse_count = int(payload["pulse_count"])
        flowing = bool(payload["flowing"])

        if previous_state:
            previous_pulse = int(previous_state.get("pulse_count", 0))
            if pulse_count + 5 < previous_pulse:
                alerts.append(
                    GeneratedAlert(
                        station_id=station_id,
                        pump_id=pump_id,
                        device_id=device_id,
                        severity=AlertSeverity.CRITICAL,
                        rule_name="sudden_meter_reset",
                        message="Pulse counter dropped abruptly, indicating a possible reset or tamper.",
                        metadata_json={"previous_pulse": previous_pulse, "current_pulse": pulse_count},
                    )
                )

            stall_count = int(previous_state.get("stall_count", 0))
            if flowing and pulse_count == previous_pulse and stall_count >= 2:
                alerts.append(
                    GeneratedAlert(
                        station_id=station_id,
                        pump_id=pump_id,
                        device_id=device_id,
                        severity=AlertSeverity.MEDIUM,
                        rule_name="pulses_stop_while_flowing",
                        message="The pump reports active flow but pulses have stopped increasing.",
                        metadata_json={"stall_count": stall_count + 1},
                    )
                )
        return alerts

    async def evaluate_transaction(
        self,
        *,
        session: AsyncSession,
        station_id: str,
        pump_id: str,
        device_id: str | None,
        payload: dict[str, Any],
    ) -> list[GeneratedAlert]:
        alerts: list[GeneratedAlert] = []
        liters = float(payload["liters"])
        pulse_count = int(payload["pulse_count"])
        duration_seconds = int(payload["duration_seconds"])

        pulses_per_liter = pulse_count / liters if liters else 0
        if liters > 0 and pulses_per_liter < EXPECTED_PULSES_PER_LITER * 0.75:
            alerts.append(
                GeneratedAlert(
                    station_id=station_id,
                    pump_id=pump_id,
                    device_id=device_id,
                    severity=AlertSeverity.CRITICAL,
                    rule_name="abnormally_low_pulses_per_liter",
                    message="Observed pulses per liter are materially below the expected calibration range.",
                    metadata_json={"pulses_per_liter": pulses_per_liter},
                )
            )

        if duration_seconds < 5 or duration_seconds > 45 * 60:
            alerts.append(
                GeneratedAlert(
                    station_id=station_id,
                    pump_id=pump_id,
                    device_id=device_id,
                    severity=AlertSeverity.MEDIUM,
                    rule_name="fueling_duration_unrealistic",
                    message="Fueling duration sits outside the expected operational range.",
                    metadata_json={"duration_seconds": duration_seconds},
                )
            )

        window_start = datetime.now(UTC) - timedelta(hours=1)
        short_tx_query: Select[tuple[Transaction]] = select(Transaction).where(
            Transaction.pump_id == pump_id,
            Transaction.end_time >= window_start,
            Transaction.duration_seconds < 15,
        )
        short_transactions = (await session.execute(short_tx_query)).scalars().all()
        if len(short_transactions) >= 4 and duration_seconds < 15:
            alerts.append(
                GeneratedAlert(
                    station_id=station_id,
                    pump_id=pump_id,
                    device_id=device_id,
                    severity=AlertSeverity.MEDIUM,
                    rule_name="too_many_short_transactions",
                    message="Pump has recorded too many very short fueling transactions in the last hour.",
                    metadata_json={"short_transactions_last_hour": len(short_transactions) + 1},
                )
            )

        return alerts

    async def evaluate_device_offline(
        self,
        *,
        session: AsyncSession,
        device: Device,
        station: Station,
    ) -> list[GeneratedAlert]:
        if device.last_heartbeat is None:
            return []
        now = datetime.now(UTC)
        if now.time() < station.active_from or now.time() > station.active_to:
            return []
        if now - device.last_heartbeat < timedelta(minutes=5):
            return []
        return [
            GeneratedAlert(
                station_id=station.id,
                pump_id=device.pump_id,
                device_id=device.id,
                severity=AlertSeverity.LOW,
                rule_name="device_offline_during_active_hours",
                message="Device heartbeat is stale during configured station active hours.",
                metadata_json={"last_heartbeat": device.last_heartbeat.isoformat()},
            )
        ]

