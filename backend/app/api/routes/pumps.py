from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip, require_roles
from app.core.enums import AuditAction, Role
from app.db.session import get_db_session, get_redis
from app.models import Pump, User
from app.schemas.pump import PumpCreate, PumpDetail, PumpRead
from app.services.audit import log_action
from app.services.dashboard import get_pump_detail

router = APIRouter()


@router.get("", response_model=list[PumpRead])
async def list_pumps(
    station_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[Pump]:
    query = select(Pump)
    if station_id:
        query = query.where(Pump.station_id == station_id)
    return (await session.execute(query)).scalars().all()


@router.post("", response_model=PumpRead, status_code=status.HTTP_201_CREATED)
async def create_pump(
    payload: PumpCreate,
    request: Request,
    current_user: User = Depends(require_roles(Role.SUPER_ADMIN, Role.MANAGER, Role.STATION_OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> Pump:
    pump = Pump(
        station_id=payload.station_id,
        name=payload.name,
        product_name=payload.product_name,
    )
    session.add(pump)
    await session.flush()
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="pump",
        entity_id=pump.id,
        details=payload.model_dump(),
        ip_address=get_request_ip(request),
    )
    await session.commit()
    await session.refresh(pump)
    return pump


@router.get("/{pump_id}", response_model=PumpDetail)
async def pump_detail(
    pump_id: str,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
    _: User = Depends(get_current_user),
) -> PumpDetail:
    return await get_pump_detail(session, redis, pump_id)
