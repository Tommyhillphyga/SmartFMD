from datetime import datetime

from pydantic import BaseModel

from app.core.enums import DeviceStatus
from app.schemas.common import AppBaseModel


class DeviceCreate(BaseModel):
    id: str
    station_id: str
    pump_id: str
    firmware_version: str = "1.0.0"


class DeviceRead(AppBaseModel):
    id: str
    station_id: str
    pump_id: str
    firmware_version: str
    status: DeviceStatus
    last_heartbeat: datetime | None
    rssi: int | None
    voltage: float | None
    battery_level: float | None
    metadata_json: dict

