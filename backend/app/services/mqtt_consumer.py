import asyncio
import json
from collections.abc import Callable

import paho.mqtt.client as mqtt
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.logging import logger
from app.services.telemetry import TelemetryIngestionService


class MQTTConsumer:
    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession],
        redis: Redis,
        ingestion_service: TelemetryIngestionService,
        loop_provider: Callable[[], asyncio.AbstractEventLoop],
    ) -> None:
        self.settings = get_settings()
        self.redis = redis
        self.session_factory = session_factory
        self.ingestion_service = ingestion_service
        self.loop_provider = loop_provider
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.settings.mqtt_username:
            self.client.username_pw_set(
                self.settings.mqtt_username,
                self.settings.mqtt_password or "",
            )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self) -> None:
        if not self.settings.mqtt_enabled:
            logger.info("MQTT consumer disabled by configuration.")
            return
        logger.info("Starting MQTT consumer on %s:%s", self.settings.mqtt_host, self.settings.mqtt_port)
        self.client.connect_async(self.settings.mqtt_host, self.settings.mqtt_port, 60)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties) -> None:  # type: ignore[no-untyped-def]
        topic = f"{self.settings.mqtt_base_topic}/+/+/#"
        logger.info("MQTT connected with reason code %s, subscribing to %s", reason_code, topic)
        client.subscribe(topic)

    def on_message(self, client, userdata, message) -> None:  # type: ignore[no-untyped-def]
        loop = self.loop_provider()
        asyncio.run_coroutine_threadsafe(self._handle_message(message.topic, message.payload), loop)

    async def _handle_message(self, topic: str, payload_bytes: bytes) -> None:
        parts = topic.split("/")
        if len(parts) < 4:
            logger.warning("Skipping malformed topic: %s", topic)
            return
        station_id = parts[1]
        event_type = parts[3]
        payload = json.loads(payload_bytes.decode("utf-8"))
        async with self.session_factory() as session:
            if event_type == "telemetry":
                await self.ingestion_service.process_telemetry(
                    session=session,
                    redis=self.redis,
                    station_id=station_id,
                    payload=payload,
                )
            elif event_type == "transaction":
                await self.ingestion_service.process_transaction(
                    session=session,
                    redis=self.redis,
                    station_id=station_id,
                    payload=payload,
                )

