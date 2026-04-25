from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip, require_roles
from app.core.enums import AuditAction, Role
from app.core.security import hash_password
from app.db.session import get_db_session
from app.models import User
from app.schemas.user import UserCreate, UserRead
from app.services.audit import log_action

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[User]:
    return (await session.execute(select(User))).scalars().all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    request: Request,
    current_user: User = Depends(require_roles(Role.SUPER_ADMIN, Role.STATION_OWNER, Role.MANAGER)),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    user = User(
        company_id=payload.company_id,
        station_id=payload.station_id,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    await session.flush()
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="user",
        entity_id=user.id,
        details={"email": payload.email, "role": payload.role.value},
        ip_address=get_request_ip(request),
    )
    await session.commit()
    await session.refresh(user)
    return user
