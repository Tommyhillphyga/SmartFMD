from datetime import datetime, time
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AlertSeverity, AlertStatus, AuditAction, DeviceStatus, PumpStatus, Role
from app.db.base import Base, NamedMixin, TimestampMixin, generate_id


class Company(TimestampMixin, NamedMixin, Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("COM"))

    stations: Mapped[list["Station"]] = relationship(back_populates="company")
    users: Mapped[list["User"]] = relationship(back_populates="company")


class Station(TimestampMixin, NamedMixin, Base):
    __tablename__ = "stations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("STA"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    active_from: Mapped[time] = mapped_column(Time(), default=time(6, 0))
    active_to: Mapped[time] = mapped_column(Time(), default=time(22, 0))
    timezone: Mapped[str] = mapped_column(String(64), default="Africa/Lagos")

    company: Mapped["Company"] = relationship(back_populates="stations")
    pumps: Mapped[list["Pump"]] = relationship(back_populates="station")
    devices: Mapped[list["Device"]] = relationship(back_populates="station")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="station")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="station")
    users: Mapped[list["User"]] = relationship(back_populates="station")


class Pump(TimestampMixin, Base):
    __tablename__ = "pumps"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("PUMP"))
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[PumpStatus] = mapped_column(Enum(PumpStatus), default=PumpStatus.IDLE)
    product_name: Mapped[str] = mapped_column(String(64), default="PMS")
    totalizer_liters: Mapped[float] = mapped_column(Float, default=0)
    totalizer_amount: Mapped[float] = mapped_column(Float, default=0)

    station: Mapped["Station"] = relationship(back_populates="pumps")
    nozzles: Mapped[list["Nozzle"]] = relationship(back_populates="pump")
    device: Mapped["Device"] = relationship(back_populates="pump", uselist=False)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="pump")
    telemetry_logs: Mapped[list["TelemetryLog"]] = relationship(back_populates="pump")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="pump")


class Nozzle(TimestampMixin, Base):
    __tablename__ = "nozzles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("NOZ"))
    pump_id: Mapped[str] = mapped_column(ForeignKey("pumps.id"), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(32), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(32), default="PMS")
    price_per_liter: Mapped[float] = mapped_column(Float, default=972)

    pump: Mapped["Pump"] = relationship(back_populates="nozzles")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="nozzle")


class Device(TimestampMixin, Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"), index=True, nullable=False)
    pump_id: Mapped[str] = mapped_column(
        ForeignKey("pumps.id"), index=True, nullable=False, unique=True
    )
    firmware_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    status: Mapped[DeviceStatus] = mapped_column(Enum(DeviceStatus), default=DeviceStatus.ONLINE)
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rssi: Mapped[int | None] = mapped_column(Integer)
    voltage: Mapped[float | None] = mapped_column(Float)
    battery_level: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    station: Mapped["Station"] = relationship(back_populates="devices")
    pump: Mapped["Pump"] = relationship(back_populates="device")
    telemetry_logs: Mapped[list["TelemetryLog"]] = relationship(back_populates="device")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="device")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("USR"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), index=True, nullable=False)
    station_id: Mapped[str | None] = mapped_column(ForeignKey("stations.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company: Mapped["Company"] = relationship(back_populates="users")
    station: Mapped["Station | None"] = relationship(back_populates="users")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="attendant")
    acknowledged_alerts: Mapped[list["Alert"]] = relationship(back_populates="acknowledged_by_user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("TXN"))
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"), index=True, nullable=False)
    pump_id: Mapped[str] = mapped_column(ForeignKey("pumps.id"), index=True, nullable=False)
    nozzle_id: Mapped[str] = mapped_column(ForeignKey("nozzles.id"), index=True, nullable=False)
    device_id: Mapped[str | None] = mapped_column(ForeignKey("devices.id"), index=True)
    attendant_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    liters: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_liter: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    pulse_count: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    station: Mapped["Station"] = relationship(back_populates="transactions")
    pump: Mapped["Pump"] = relationship(back_populates="transactions")
    nozzle: Mapped["Nozzle"] = relationship(back_populates="transactions")
    attendant: Mapped["User | None"] = relationship(back_populates="transactions")


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=lambda: generate_id("TEL")
    )
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"), index=True, nullable=False)
    pump_id: Mapped[str] = mapped_column(ForeignKey("pumps.id"), index=True, nullable=False)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    pulse_count: Mapped[int] = mapped_column(Integer, nullable=False)
    flowing: Mapped[bool] = mapped_column(Boolean, default=False)
    voltage: Mapped[float | None] = mapped_column(Float)
    rssi: Mapped[int | None] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    pump: Mapped["Pump"] = relationship(back_populates="telemetry_logs")
    device: Mapped["Device"] = relationship(back_populates="telemetry_logs")

    __table_args__ = (
        Index("ix_telemetry_logs_station_pump_timestamp", "station_id", "pump_id", "timestamp"),
    )


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("ALT"))
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"), index=True, nullable=False)
    pump_id: Mapped[str | None] = mapped_column(ForeignKey("pumps.id"), index=True)
    device_id: Mapped[str | None] = mapped_column(ForeignKey("devices.id"), index=True)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.OPEN)
    rule_name: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))

    station: Mapped["Station"] = relationship(back_populates="alerts")
    pump: Mapped["Pump | None"] = relationship(back_populates="alerts")
    device: Mapped["Device | None"] = relationship(back_populates="alerts")
    acknowledged_by_user: Mapped["User | None"] = relationship(back_populates="acknowledged_alerts")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("AUD"))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    user: Mapped["User | None"] = relationship(back_populates="audit_logs")


__all__ = [
    "Alert",
    "AuditLog",
    "Company",
    "Device",
    "Nozzle",
    "Pump",
    "Station",
    "TelemetryLog",
    "Transaction",
    "User",
]

