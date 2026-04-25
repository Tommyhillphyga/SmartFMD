from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip
from app.core.enums import AuditAction
from app.db.session import get_db_session
from app.models import User
from app.schemas.auth import AuthResponse, AuthUser, LoginRequest, RefreshRequest
from app.services.audit import log_action
from app.services.auth import authenticate_user, build_auth_response, refresh_access_token

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    user = await authenticate_user(session, payload.email, payload.password)
    await log_action(
        session,
        user_id=user.id,
        action=AuditAction.LOGIN,
        entity_type="auth",
        entity_id=user.id,
        ip_address=get_request_ip(request),
    )
    await session.commit()
    return build_auth_response(user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    return await refresh_access_token(session, payload.refresh_token)


@router.get("/me", response_model=AuthUser)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
