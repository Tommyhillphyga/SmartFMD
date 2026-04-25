from pydantic import BaseModel, Field

from app.core.enums import PumpStatus
from app.schemas.common import AppBaseModel


class PumpCreate(BaseModel):
    station_id: str
    name: str
    product_name: str = "PMS"


class PumpRead(AppBaseModel):
    id: str
    station_id: str
    name: str
    status: PumpStatus
    product_name: str
    totalizer_liters: float
    totalizer_amount: float


class PumpDetail(PumpRead):
    latest_telemetry: dict | None = None
    active_transactions: list[dict] = Field(default_factory=list)
    device: dict | None = None
