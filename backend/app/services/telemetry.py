from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertStatus, DeviceStatus, PumpStatus
from app.core.logging import logger
from app.metrics.registry import alerts_total, telemetry_messages_total, transactions_total
from app.models import Alert, Device, Nozzle, Pump, Station, TelemetryLog, Transaction, User
from app.services.cache import CacheService
from app.services.fraud_engine import FraudEngine, GeneratedAlert
from app.services.notifications import queue_alert_notifications
from app.services.websocket_manager import WebSocketManager


class TelemetryPayload(BaseModel):
    device_id: str
    pump_id: str
    pulse_count: int = Field(ge=0)
    flowing: bool
    voltage: float | None = None
    rssi: int | None = None
    timestamp: datetime


class TransactionPayload(BaseModel):
    pump_id: str
    liters: float = Field(gt=0)
    amount: float = Field(gt=0)
    price_per_liter: float = Field(gt=0)
    pulse_count: int = Field(ge=0)
    duration_seconds: int = Field(gt=0)
    attendant_id: str | None = None
    timestamp: datetime


class TelemetryIngestionService:
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.fraud_engine = FraudEngine()

    async def process_telemetry(
        self,
        *,
        session: AsyncSession,
        redis: Redis,
        station_id: str,
        payload: dict[str, Any],
    ) -> TelemetryLog:
        parsed = TelemetryPayload.model_validate(payload)
        pump = (await session.execute(select(Pump).where(Pump.id == parsed.pump_id))).scalar_one()
        device = (
            await session.execute(select(Device).where(Device.id == parsed.device_id))
        ).scalar_one_or_none()
        if device is None:
            device = Device(
                id=parsed.device_id,
                station_id=station_id,
                pump_id=parsed.pump_id,
                firmware_version="1.0.0",
            )
            session.add(device)

        telemetry = TelemetryLog(
            station_id=station_id,
            pump_id=parsed.pump_id,
            device_id=parsed.device_id,
            pulse_count=parsed.pulse_count,
            flowing=parsed.flowing,
            voltage=parsed.voltage,
            rssi=parsed.rssi,
            timestamp=parsed.timestamp,
        )
        session.add(telemetry)

        device.last_heartbeat = parsed.timestamp
        device.rssi = parsed.rssi
        device.voltage = parsed.voltage
        device.status = DeviceStatus.ONLINE
        pump.status = PumpStatus.FUELING if parsed.flowing else PumpStatus.IDLE

        cache = CacheService(redis)
        previous_state = await cache.get_live_pump(station_id, parsed.pump_id)
        stall_count = 0
        if previous_state and parsed.flowing and previous_state.get("pulse_count") == parsed.pulse_count:
            stall_count = int(previous_state.get("stall_count", 0)) + 1

        alerts = await self.fraud_engine.evaluate_telemetry(
            session=session,
            station_id=station_id,
            pump_id=parsed.pump_id,
            device_id=parsed.device_id,
            payload=parsed.model_dump(),
            previous_state=previous_state,
        )
        created_alerts = await self._persist_alerts(session, alerts)

        await cache.set_live_pump(
            station_id,
            parsed.pump_id,
            {
                "device_id": parsed.device_id,
                "pump_id": parsed.pump_id,
                "pulse_count": parsed.pulse_count,
                "flowing": parsed.flowing,
                "voltage": parsed.voltage,
                "rssi": parsed.rssi,
                "timestamp": parsed.timestamp,
                "stall_count": stall_count,
            },
        )

        await session.commit()
        telemetry_messages_total.inc()
        await self.websocket_manager.broadcast(
            station_id,
            {
                "event": "telemetry",
                "station_id": station_id,
                "pump_id": parsed.pump_id,
                "payload": {
                    "pulse_count": parsed.pulse_count,
                    "flowing": parsed.flowing,
                    "voltage": parsed.voltage,
                    "rssi": parsed.rssi,
                    "timestamp": parsed.timestamp.isoformat(),
                },
            },
        )
        for alert in created_alerts:
            await self.websocket_manager.broadcast(
                station_id,
                {"event": "alert", "station_id": station_id, "payload": alert.message},
            )
        return telemetry

    async def process_transaction(
        self,
        *,
        session: AsyncSession,
        redis: Redis,
        station_id: str,
        payload: dict[str, Any],
    ) -> Transaction:
        parsed = TransactionPayload.model_validate(payload)
        pump = (await session.execute(select(Pump).where(Pump.id == parsed.pump_id))).scalar_one()
        nozzle = (
            await session.execute(select(Nozzle).where(Nozzle.pump_id == parsed.pump_id))
        ).scalars().first()
        if nozzle is None:
            nozzle = Nozzle(
                pump_id=parsed.pump_id,
                label="A",
                price_per_liter=parsed.price_per_liter,
            )
            session.add(nozzle)
            await session.flush()
        device = (
            await session.execute(select(Device).where(Device.pump_id == parsed.pump_id))
        ).scalar_one_or_none()
        attendant = None
        if parsed.attendant_id:
            attendant = (
                await session.execute(select(User).where(User.id == parsed.attendant_id))
            ).scalar_one_or_none()

        transaction = Transaction(
            station_id=station_id,
            pump_id=parsed.pump_id,
            nozzle_id=nozzle.id,
            device_id=device.id if device else None,
            attendant_id=attendant.id if attendant else None,
            start_time=parsed.timestamp - timedelta(seconds=parsed.duration_seconds),
            end_time=parsed.timestamp,
            liters=parsed.liters,
            price_per_liter=parsed.price_per_liter,
            amount=parsed.amount,
            pulse_count=parsed.pulse_count,
            duration_seconds=parsed.duration_seconds,
            metadata_json={"source_attendant_id": parsed.attendant_id} if parsed.attendant_id else {},
        )
        session.add(transaction)

        pump.totalizer_liters += parsed.liters
        pump.totalizer_amount += parsed.amount
        pump.status = PumpStatus.IDLE

        alerts = await self.fraud_engine.evaluate_transaction(
            session=session,
            station_id=station_id,
            pump_id=parsed.pump_id,
            device_id=device.id if device else None,
            payload=parsed.model_dump(),
        )
        created_alerts = await self._persist_alerts(session, alerts)

        cache = CacheService(redis)
        live_state = await cache.get_live_pump(station_id, parsed.pump_id) or {}
        live_state.update(
            {
                "flowing": False,
                "timestamp": parsed.timestamp,
                "pulse_count": parsed.pulse_count,
                "last_transaction_amount": parsed.amount,
                "last_transaction_liters": parsed.liters,
                "stall_count": 0,
            }
        )
        await cache.set_live_pump(station_id, parsed.pump_id, live_state)

        await session.commit()
        transactions_total.inc()
        await self.websocket_manager.broadcast(
            station_id,
            {
                "event": "transaction_completed",
                "station_id": station_id,
                "pump_id": parsed.pump_id,
                "payload": {
                    "liters": parsed.liters,
                    "amount": parsed.amount,
                    "pulse_count": parsed.pulse_count,
                    "duration_seconds": parsed.duration_seconds,
                    "timestamp": parsed.timestamp.isoformat(),
                },
            },
        )
        for alert in created_alerts:
            await self.websocket_manager.broadcast(
                station_id,
                {"event": "alert", "station_id": station_id, "payload": alert.message},
            )
        return transaction

    async def scan_for_offline_devices(self, session: AsyncSession) -> list[Alert]:
        devices = (await session.execute(select(Device))).scalars().all()
        created: list[Alert] = []
        for device in devices:
            station = (await session.execute(select(Station).where(Station.id == device.station_id))).scalar_one()
            alerts = await self.fraud_engine.evaluate_device_offline(
                session=session,
                device=device,
                station=station,
            )
            created.extend(await self._persist_alerts(session, alerts))
        if created:
            await session.commit()
        return created

    async def _persist_alerts(
        self,
        session: AsyncSession,
        alerts: list[GeneratedAlert],
    ) -> list[Alert]:
        created: list[Alert] = []
        for generated in alerts:
            existing = (
                await session.execute(
                    select(Alert).where(
                        and_(
                            Alert.station_id == generated.station_id,
                            Alert.pump_id == generated.pump_id,
                            Alert.rule_name == generated.rule_name,
                            Alert.status == AlertStatus.OPEN,
                        )
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                continue
            alert = Alert(
                station_id=generated.station_id,
                pump_id=generated.pump_id,
                device_id=generated.device_id,
                severity=generated.severity,
                rule_name=generated.rule_name,
                message=generated.message,
                metadata_json=generated.metadata_json,
            )
            session.add(alert)
            await session.flush()
            alerts_total.labels(
                severity=generated.severity.value, rule_name=generated.rule_name
            ).inc()
            created.append(alert)
            try:
                queue_alert_notifications(alert)
            except Exception as exc:
                logger.warning("Failed to enqueue alert notification: %s", exc)
        return created
