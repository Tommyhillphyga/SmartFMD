from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import AppBaseModel


class TransactionCreate(BaseModel):
    station_id: str
    pump_id: str
    nozzle_id: str
    device_id: str | None = None
    attendant_id: str | None = None
    start_time: datetime
    end_time: datetime
    liters: float = Field(gt=0)
    price_per_liter: float = Field(gt=0)
    amount: float = Field(gt=0)
    pulse_count: int = Field(ge=0)
    duration_seconds: int = Field(gt=0)
    metadata_json: dict = Field(default_factory=dict)


class TransactionRead(AppBaseModel):
    id: str
    station_id: str
    pump_id: str
    nozzle_id: str
    device_id: str | None
    attendant_id: str | None
    start_time: datetime
    end_time: datetime
    liters: float
    price_per_liter: float
    amount: float
    pulse_count: int
    duration_seconds: int
    metadata_json: dict

