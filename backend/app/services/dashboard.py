from collections import defaultdict
from datetime import UTC, datetime

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import Role
from app.models import Alert, Pump, Station, Transaction, User
from app.schemas.alert import AlertRead
from app.schemas.pump import PumpDetail
from app.schemas.station import DashboardOverview, PumpSnapshot, StationDashboard, StationRead
from app.services.cache import CacheService


async def _accessible_stations(session: AsyncSession, user: User) -> list[Station]:
    query = select(Station)
    if user.role == Role.SUPER_ADMIN:
        return (await session.execute(query)).scalars().all()
    if user.station_id:
        query = query.where(Station.id == user.station_id)
    else:
        query = query.where(Station.company_id == user.company_id)
    return (await session.execute(query)).scalars().all()


async def get_dashboard_overview(
    session: AsyncSession,
    redis: Redis,
    current_user: User,
) -> DashboardOverview:
    stations = await _accessible_stations(session, current_user)
    station_ids = {station.id for station in stations}
    transactions = (await session.execute(select(Transaction))).scalars().all()
    alerts = (await session.execute(select(Alert))).scalars().all()
    today = datetime.now(UTC).date()

    liters_today = 0.0
    revenue_today = 0.0
    open_alerts = 0
    active_sessions = 0
    daily_totals = defaultdict(lambda: {"liters": 0.0, "revenue": 0.0, "alerts": 0})
    recent_alerts: list[AlertRead] = []

    for transaction in transactions:
        if transaction.station_id not in station_ids:
            continue
        date_key = transaction.end_time.date().isoformat()
        daily_totals[date_key]["liters"] += transaction.liters
        daily_totals[date_key]["revenue"] += transaction.amount
        if transaction.end_time.date() == today:
            liters_today += transaction.liters
            revenue_today += transaction.amount

    filtered_alerts = [alert for alert in alerts if alert.station_id in station_ids]
    filtered_alerts.sort(key=lambda alert: alert.created_at, reverse=True)
    open_alerts = sum(1 for alert in filtered_alerts if alert.status.value == "open")
    for alert in filtered_alerts[:5]:
        recent_alerts.append(AlertRead.model_validate(alert))
        daily_totals[alert.created_at.date().isoformat()]["alerts"] += 1

    cache = CacheService(redis)
    for station in stations:
        station_pumps = (await session.execute(select(Pump).where(Pump.station_id == station.id))).scalars().all()
        for pump in station_pumps:
            live = await cache.get_live_pump(station.id, pump.id)
            if live and live.get("flowing"):
                active_sessions += 1

    trend_keys = sorted(daily_totals.keys())[-7:]
    trends = [
        {
            "label": key,
            "liters": round(daily_totals[key]["liters"], 2),
            "revenue": round(daily_totals[key]["revenue"], 2),
            "alerts": daily_totals[key]["alerts"],
        }
        for key in trend_keys
    ]
    return DashboardOverview(
        active_sessions=active_sessions,
        liters_today=round(liters_today, 2),
        revenue_today=round(revenue_today, 2),
        open_alerts=open_alerts,
        stations=[StationRead.model_validate(station) for station in stations],
        recent_alerts=recent_alerts,
        trends=trends,
    )


async def get_station_dashboard(
    session: AsyncSession,
    redis: Redis,
    station_id: str,
    current_user: User,
) -> StationDashboard:
    station_query = select(Station).where(Station.id == station_id)
    if current_user.role != Role.SUPER_ADMIN:
        if current_user.station_id:
            station_query = station_query.where(Station.id == current_user.station_id)
        else:
            station_query = station_query.where(Station.company_id == current_user.company_id)
    station = (await session.execute(station_query)).scalar_one_or_none()
    if station is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    pumps = (await session.execute(select(Pump).where(Pump.station_id == station_id))).scalars().all()
    transactions = (
        await session.execute(select(Transaction).where(Transaction.station_id == station_id))
    ).scalars().all()
    alerts = (await session.execute(select(Alert).where(Alert.station_id == station_id))).scalars().all()
    today = datetime.now(UTC).date()
    by_pump = defaultdict(lambda: {"liters": 0.0, "revenue": 0.0, "count": 0})
    for transaction in transactions:
        if transaction.end_time.date() == today:
            by_pump[transaction.pump_id]["liters"] += transaction.liters
            by_pump[transaction.pump_id]["revenue"] += transaction.amount
            by_pump[transaction.pump_id]["count"] += 1

    cache = CacheService(redis)
    snapshots: list[PumpSnapshot] = []
    active_sessions = 0
    for pump in pumps:
        live = await cache.get_live_pump(station_id, pump.id)
        if live and live.get("flowing"):
            active_sessions += 1
        snapshots.append(
            PumpSnapshot(
                id=pump.id,
                name=pump.name,
                status=pump.status,
                liters_today=round(by_pump[pump.id]["liters"], 2),
                revenue_today=round(by_pump[pump.id]["revenue"], 2),
                current_pulse_count=live.get("pulse_count") if live else None,
                device_id=live.get("device_id") if live else None,
                last_seen=live.get("timestamp") if live else None,
            )
        )

    return StationDashboard(
        station=StationRead.model_validate(station),
        pumps=snapshots,
        active_sessions=active_sessions,
        liters_today=round(sum(item["liters"] for item in by_pump.values()), 2),
        revenue_today=round(sum(item["revenue"] for item in by_pump.values()), 2),
        alerts_open=sum(1 for alert in alerts if alert.status.value == "open"),
        transaction_count_today=sum(item["count"] for item in by_pump.values()),
    )


async def get_pump_detail(session: AsyncSession, redis: Redis, pump_id: str) -> PumpDetail:
    pump = (await session.execute(select(Pump).where(Pump.id == pump_id))).scalar_one_or_none()
    if pump is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pump not found")
    cache = CacheService(redis)
    live = await cache.get_live_pump(pump.station_id, pump.id)
    return PumpDetail(
        id=pump.id,
        station_id=pump.station_id,
        name=pump.name,
        status=pump.status,
        product_name=pump.product_name,
        totalizer_liters=pump.totalizer_liters,
        totalizer_amount=pump.totalizer_amount,
        latest_telemetry=live,
        active_transactions=[live] if live and live.get("flowing") else [],
        device={"id": live.get("device_id")} if live else None,
    )
