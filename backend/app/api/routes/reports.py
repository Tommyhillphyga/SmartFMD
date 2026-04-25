from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_request_ip
from app.core.enums import AuditAction
from app.db.session import get_db_session
from app.models import User
from app.schemas.report import ReportSummary
from app.services.audit import log_action
from app.services.reports import build_report_summary, export_report_pdf, export_transactions_csv

router = APIRouter()


@router.get("/overview", response_model=ReportSummary)
async def overview(
    station_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> ReportSummary:
    return await build_report_summary(session, station_id)


@router.get("/export/csv")
async def export_csv(
    request: Request,
    station_id: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    payload = await export_transactions_csv(session, station_id)
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.EXPORT,
        entity_type="report_csv",
        details={"station_id": station_id},
        ip_address=get_request_ip(request),
    )
    await session.commit()
    return Response(
        content=payload,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/export/pdf")
async def export_pdf(
    request: Request,
    station_id: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    payload = await export_report_pdf(session, station_id)
    await log_action(
        session,
        user_id=current_user.id,
        action=AuditAction.EXPORT,
        entity_type="report_pdf",
        details={"station_id": station_id},
        ip_address=get_request_ip(request),
    )
    await session.commit()
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analytics-summary.pdf"},
    )

