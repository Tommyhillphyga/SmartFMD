from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(AppBaseModel):
    message: str


class PaginatedResponse(AppBaseModel):
    total: int
    items: list


class TimeSeriesPoint(AppBaseModel):
    label: str
    liters: float = 0
    revenue: float = 0
    alerts: int = 0


class AuditLogRead(AppBaseModel):
    id: str
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict
    ip_address: str | None
    timestamp: datetime

