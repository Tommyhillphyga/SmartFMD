from datetime import time

from pydantic import BaseModel

from app.core.enums import PumpStatus
from app.schemas.common import AppBaseModel, TimeSeriesPoint


class StationCreate(BaseModel):
    company_id: str
    name: str
    location: str
    city: str
    active_from: time | None = None
    active_to: time | None = None


class StationRead(AppBaseModel):
    id: str
    company_id: str
    name: str
    location: str
    city: str
    timezone: str


class PumpSnapshot(AppBaseModel):
    id: str
    name: str
    status: PumpStatus
    liters_today: float
    revenue_today: float
    current_pulse_count: int | None = None
    device_id: str | None = None
    last_seen: str | None = None


class DashboardOverview(AppBaseModel):
    active_sessions: int
    liters_today: float
    revenue_today: float
    open_alerts: int
    stations: list[StationRead]
    recent_alerts: list
    trends: list[TimeSeriesPoint]


class StationDashboard(AppBaseModel):
    station: StationRead
    pumps: list[PumpSnapshot]
    active_sessions: int
    liters_today: float
    revenue_today: float
    alerts_open: int
    transaction_count_today: int

