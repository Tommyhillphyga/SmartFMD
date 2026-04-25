import csv
import io
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Alert, Pump, Station, Transaction, User
from app.schemas.report import ReportSummary


def _daterange(days: int) -> list[date]:
    today = datetime.now(UTC).date()
    start = today - timedelta(days=days - 1)
    return [start + timedelta(days=offset) for offset in range(days)]


async def build_report_summary(session: AsyncSession, station_id: str | None = None) -> ReportSummary:
    tx_query = select(Transaction)
    alert_query = select(Alert)
    if station_id:
        tx_query = tx_query.where(Transaction.station_id == station_id)
        alert_query = alert_query.where(Alert.station_id == station_id)

    transactions = (await session.execute(tx_query)).scalars().all()
    alerts = (await session.execute(alert_query)).scalars().all()
    pumps = (await session.execute(select(Pump))).scalars().all()
    stations = (await session.execute(select(Station))).scalars().all()
    users = (await session.execute(select(User))).scalars().all()

    liters_by_day = defaultdict(float)
    revenue_by_day = defaultdict(float)
    alerts_by_day = defaultdict(int)
    pump_totals = defaultdict(lambda: {"liters": 0.0, "revenue": 0.0})
    station_totals = defaultdict(float)
    user_totals = defaultdict(lambda: {"transactions": 0, "revenue": 0.0})

    for transaction in transactions:
        key = transaction.end_time.date().isoformat()
        liters_by_day[key] += transaction.liters
        revenue_by_day[key] += transaction.amount
        pump_totals[transaction.pump_id]["liters"] += transaction.liters
        pump_totals[transaction.pump_id]["revenue"] += transaction.amount
        station_totals[transaction.station_id] += transaction.amount
        if transaction.attendant_id:
            user_totals[transaction.attendant_id]["transactions"] += 1
            user_totals[transaction.attendant_id]["revenue"] += transaction.amount

    for alert in alerts:
        alerts_by_day[alert.created_at.date().isoformat()] += 1

    daily_liters_sold = [
        {"label": day.isoformat(), "liters": round(liters_by_day[day.isoformat()], 2)}
        for day in _daterange(7)
    ]
    daily_revenue = [
        {"label": day.isoformat(), "revenue": round(revenue_by_day[day.isoformat()], 2)}
        for day in _daterange(7)
    ]
    anomaly_trends = [
        {"label": day.isoformat(), "alerts": alerts_by_day[day.isoformat()]}
        for day in _daterange(7)
    ]
    pump_comparison = [
        {
            "pump_id": pump.id,
            "name": pump.name,
            "liters": round(pump_totals[pump.id]["liters"], 2),
            "revenue": round(pump_totals[pump.id]["revenue"], 2),
        }
        for pump in pumps
    ]
    station_ranking = sorted(
        [
            {
                "station_id": station.id,
                "name": station.name,
                "revenue": round(station_totals[station.id], 2),
            }
            for station in stations
        ],
        key=lambda item: item["revenue"],
        reverse=True,
    )
    user_lookup = {user.id: user for user in users}
    attendant_productivity = sorted(
        [
            {
                "attendant_id": attendant_id,
                "name": user_lookup.get(attendant_id).full_name
                if user_lookup.get(attendant_id)
                else attendant_id,
                "transactions": totals["transactions"],
                "revenue": round(totals["revenue"], 2),
            }
            for attendant_id, totals in user_totals.items()
        ],
        key=lambda item: item["revenue"],
        reverse=True,
    )

    return ReportSummary(
        daily_liters_sold=daily_liters_sold,
        daily_revenue=daily_revenue,
        pump_comparison=pump_comparison,
        station_ranking=station_ranking,
        anomaly_trends=anomaly_trends,
        attendant_productivity=attendant_productivity,
    )


async def export_transactions_csv(session: AsyncSession, station_id: str | None = None) -> bytes:
    query = select(Transaction)
    if station_id:
        query = query.where(Transaction.station_id == station_id)
    transactions = (await session.execute(query)).scalars().all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "station_id",
            "pump_id",
            "nozzle_id",
            "attendant_id",
            "start_time",
            "end_time",
            "liters",
            "amount",
            "pulse_count",
            "duration_seconds",
        ]
    )
    for transaction in transactions:
        writer.writerow(
            [
                transaction.id,
                transaction.station_id,
                transaction.pump_id,
                transaction.nozzle_id,
                transaction.attendant_id or "",
                transaction.start_time.isoformat(),
                transaction.end_time.isoformat(),
                transaction.liters,
                transaction.amount,
                transaction.pulse_count,
                transaction.duration_seconds,
            ]
        )
    return buffer.getvalue().encode("utf-8")


async def export_report_pdf(session: AsyncSession, station_id: str | None = None) -> bytes:
    summary = await build_report_summary(session, station_id)
    body_lines = [
        "SMART FUEL DISPENSER MONITORING DASHBOARD",
        "Analytics Summary",
        "",
        f"Daily liters points: {len(summary.daily_liters_sold)}",
        f"Daily revenue points: {len(summary.daily_revenue)}",
        f"Open anomaly trend points: {len(summary.anomaly_trends)}",
        f"Top station: {summary.station_ranking[0]['name'] if summary.station_ranking else 'N/A'}",
    ]
    text = " | ".join(body_lines).replace("(", "[").replace(")", "]")
    stream = f"BT /F1 14 Tf 50 760 Td ({text}) Tj ET"
    pdf = (
        "%PDF-1.4\n"
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        "2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n"
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj\n"
        "xref\n0 6\n0000000000 65535 f \n"
        "0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n"
        "0000000248 00000 n \n0000000318 00000 n \n"
        "trailer << /Root 1 0 R /Size 6 >>\nstartxref\n420\n%%EOF"
    )
    return pdf.encode("utf-8")
