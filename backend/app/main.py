import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, logger
from app.core.rate_limit import RateLimitMiddleware
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine, redis_client
from app.services.mqtt_consumer import MQTTConsumer
from app.services.runtime import telemetry_service, websocket_manager

settings = get_settings()


async def _offline_monitor(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        async with AsyncSessionLocal() as session:
            await telemetry_service.scan_for_offline_devices(session)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=60)
        except TimeoutError:
            continue


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    stop_event = asyncio.Event()
    if settings.app_auto_create_schema:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    loop = asyncio.get_running_loop()
    mqtt_consumer = MQTTConsumer(
        session_factory=AsyncSessionLocal,
        redis=redis_client,
        ingestion_service=telemetry_service,
        loop_provider=lambda: loop,
    )
    mqtt_consumer.start()
    offline_monitor_task = asyncio.create_task(_offline_monitor(stop_event))
    try:
        yield
    finally:
        stop_event.set()
        offline_monitor_task.cancel()
        mqtt_consumer.stop()
        await redis_client.aclose()
        await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=240)
app.include_router(api_router)


@app.websocket("/ws/dashboard/{station_id}")
async def dashboard_socket(websocket: WebSocket, station_id: str) -> None:
    await websocket_manager.connect(station_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(station_id, websocket)


@app.get("/")
async def root() -> dict:
    return {"name": settings.project_name, "status": "ok"}
