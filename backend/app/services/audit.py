from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction
from app.models import AuditLog


async def log_action(
    session: AsyncSession,
    *,
    user_id: str | None,
    action: AuditAction,
    entity_type: str,
    entity_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip_address,
        timestamp=datetime.now(UTC),
    )
    session.add(audit_log)
    await session.flush()
    return audit_log

