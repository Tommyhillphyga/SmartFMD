from datetime import time

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip, require_roles
from app.core.enums import AuditAction, Role
from app.db.session import get_db_session, get_redis
from app.models import Station, User
from app.schemas.station import DashboardOverview, StationCreate, StationDashboard, StationRead
from app.services.audit import log_action
from app.services.dashboard import get_dashboard_overview, get_station_dashboard

router = APIRouter()


@router.get("", response_model=list[StationRead])
async def list_stations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[Station]:
    query = select(Station)
    if current_user.role != Role.SUPER_ADMIN:
        if current_user.station_id:
            query = query.where(Station.id == current_user.station_id)
        else:
            query = query.where(Station.company_id == current_user.company_id)
    return (await session.execute(query)).scalars().all()


@router.post("", response_model=StationRead, status_code=status.HTTP_201_CREATED)
async def create_station(
    payload: StationCreate,
    request: Request,
    current_user: User = Depends(require_roles(Role.SUPER_ADMIN, Role.STATION_OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> Station:
    station = Station(
        company_id=payload.company_id,
        name=payload.name,
        location=payload.location,
        city=payload.city,
        active_from=payload.active_from or time(6, 0),
        active_to=payload.active_to or time(22, 0),
    )
    session.add(station)
    await session.flush()
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="station",
        entity_id=station.id,
        details=payload.model_dump(),
        ip_address=get_request_ip(request),
    )
    await session.commit()
    await session.refresh(station)
    return station


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> DashboardOverview:
    return await get_dashboard_overview(session, redis, current_user)


@router.get("/{station_id}", response_model=StationDashboard)
async def station_detail(
    station_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> StationDashboard:
    return await get_station_dashboard(session, redis, station_id, current_user)
