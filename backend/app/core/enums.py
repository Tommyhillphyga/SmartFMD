from enum import Enum


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    STATION_OWNER = "station_owner"
    MANAGER = "manager"
    ATTENDANT = "attendant"
    AUDITOR = "auditor"


class PumpStatus(str, Enum):
    IDLE = "idle"
    FUELING = "fueling"
    OFFLINE = "offline"
    TAMPERED = "tampered"
    ERROR = "error"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class AuditAction(str, Enum):
    LOGIN = "login"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    ACKNOWLEDGE = "acknowledge"

