from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip, require_roles
from app.core.enums import AuditAction, Role
from app.db.session import get_db_session
from app.models import Device, User
from app.schemas.device import DeviceCreate, DeviceRead
from app.services.audit import log_action

router = APIRouter()


@router.get("", response_model=list[DeviceRead])
async def list_devices(
    station_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[Device]:
    query = select(Device)
    if station_id:
        query = query.where(Device.station_id == station_id)
    return (await session.execute(query)).scalars().all()


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    payload: DeviceCreate,
    request: Request,
    current_user: User = Depends(require_roles(Role.SUPER_ADMIN, Role.MANAGER, Role.STATION_OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> Device:
    device = Device(
        id=payload.id,
        station_id=payload.station_id,
        pump_id=payload.pump_id,
        firmware_version=payload.firmware_version,
    )
    session.add(device)
    await session.flush()
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="device",
        entity_id=device.id,
        details=payload.model_dump(),
        ip_address=get_request_ip(request),
    )
    await session.commit()
    await session.refresh(device)
    return device
