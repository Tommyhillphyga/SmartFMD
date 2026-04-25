from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip
from app.core.enums import AlertSeverity, AlertStatus, AuditAction
from app.db.session import get_db_session
from app.models import Alert, User
from app.schemas.alert import AlertAcknowledgeRequest, AlertRead
from app.schemas.common import MessageResponse
from app.services.audit import log_action

router = APIRouter()


@router.get("", response_model=list[AlertRead])
async def list_alerts(
    station_id: str | None = None,
    severity: AlertSeverity | None = None,
    status: AlertStatus | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[Alert]:
    query = select(Alert).order_by(Alert.created_at.desc())
    if station_id:
        query = query.where(Alert.station_id == station_id)
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    return (await session.execute(query)).scalars().all()


@router.post("/{alert_id}/acknowledge", response_model=MessageResponse)
async def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    alert = (await session.execute(select(Alert).where(Alert.id == alert_id))).scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.now(UTC)
    alert.acknowledged_by = current_user.id
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.ACKNOWLEDGE,
        entity_type="alert",
        entity_id=alert.id,
        details={"comment": payload.comment},
        ip_address=get_request_ip(request),
    )
    await session.commit()
    return MessageResponse(message="Alert acknowledged")
