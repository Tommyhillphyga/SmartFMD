from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip
from app.core.enums import AuditAction
from app.db.session import get_db_session, get_redis
from app.models import Transaction, User
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.audit import log_action
from app.services.runtime import telemetry_service

router = APIRouter()


@router.get("", response_model=list[TransactionRead])
async def list_transactions(
    station_id: str | None = None,
    pump_id: str | None = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[Transaction]:
    query = select(Transaction).order_by(Transaction.end_time.desc()).limit(limit)
    if station_id:
        query = query.where(Transaction.station_id == station_id)
    if pump_id:
        query = query.where(Transaction.pump_id == pump_id)
    return (await session.execute(query)).scalars().all()


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> Transaction:
    transaction = await telemetry_service.process_transaction(
        session=session,
        redis=redis,
        station_id=payload.station_id,
        payload={
            "pump_id": payload.pump_id,
            "liters": payload.liters,
            "amount": payload.amount,
            "price_per_liter": payload.price_per_liter,
            "pulse_count": payload.pulse_count,
            "duration_seconds": payload.duration_seconds,
            "attendant_id": payload.attendant_id,
            "timestamp": payload.end_time or datetime.now(UTC),
        },
    )
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="transaction",
        entity_id=transaction.id,
        details=payload.model_dump(mode="json"),
        ip_address=get_request_ip(request),
    )
    await session.commit()
    await session.refresh(transaction)
    return transaction
