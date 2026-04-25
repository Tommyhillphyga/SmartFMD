from datetime import datetime

from pydantic import BaseModel

from app.core.enums import AlertSeverity, AlertStatus
from app.schemas.common import AppBaseModel


class AlertRead(AppBaseModel):
    id: str
    station_id: str
    pump_id: str | None
    device_id: str | None
    severity: AlertSeverity
    status: AlertStatus
    rule_name: str
    message: str
    metadata_json: dict
    created_at: datetime
    acknowledged_at: datetime | None
    acknowledged_by: str | None


class AlertAcknowledgeRequest(BaseModel):
    comment: str | None = None

