"""initial schema

Revision ID: 20260424_0001
Revises:
Create Date: 2026-04-24 20:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260424_0001"
down_revision = None
branch_labels = None
depends_on = None


role_enum = sa.Enum(
    "super_admin",
    "station_owner",
    "manager",
    "attendant",
    "auditor",
    name="role_enum",
)
pump_status_enum = sa.Enum(
    "idle",
    "fueling",
    "offline",
    "tampered",
    "error",
    name="pump_status_enum",
)
alert_severity_enum = sa.Enum("low", "medium", "critical", name="alert_severity_enum")
alert_status_enum = sa.Enum(
    "open",
    "acknowledged",
    "resolved",
    name="alert_status_enum",
)
device_status_enum = sa.Enum(
    "online",
    "offline",
    "degraded",
    name="device_status_enum",
)
audit_action_enum = sa.Enum(
    "login",
    "create",
    "update",
    "delete",
    "export",
    "acknowledge",
    name="audit_action_enum",
)


def upgrade() -> None:
    bind = op.get_bind()
    role_enum.create(bind, checkfirst=True)
    pump_status_enum.create(bind, checkfirst=True)
    alert_severity_enum.create(bind, checkfirst=True)
    alert_status_enum.create(bind, checkfirst=True)
    device_status_enum.create(bind, checkfirst=True)
    audit_action_enum.create(bind, checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "stations",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("company_id", sa.String(length=32), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("active_from", sa.Time(), nullable=False),
        sa.Column("active_to", sa.Time(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="Africa/Lagos"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_stations_company_id", "stations", ["company_id"])
    op.create_table(
        "pumps",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", pump_status_enum, nullable=False, server_default="idle"),
        sa.Column("product_name", sa.String(length=64), nullable=False, server_default="PMS"),
        sa.Column("totalizer_liters", sa.Float(), nullable=False, server_default="0"),
        sa.Column("totalizer_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_pumps_station_id", "pumps", ["station_id"])
    op.create_table(
        "nozzles",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("pump_id", sa.String(length=32), sa.ForeignKey("pumps.id"), nullable=False),
        sa.Column("label", sa.String(length=32), nullable=False),
        sa.Column("fuel_type", sa.String(length=32), nullable=False, server_default="PMS"),
        sa.Column("price_per_liter", sa.Float(), nullable=False, server_default="972"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nozzles_pump_id", "nozzles", ["pump_id"])
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("pump_id", sa.String(length=32), sa.ForeignKey("pumps.id"), nullable=False),
        sa.Column("firmware_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("status", device_status_enum, nullable=False, server_default="online"),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True)),
        sa.Column("rssi", sa.Integer()),
        sa.Column("voltage", sa.Float()),
        sa.Column("battery_level", sa.Float()),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("pump_id", name="uq_devices_pump_id"),
    )
    op.create_index("ix_devices_station_id", "devices", ["station_id"])
    op.create_index("ix_devices_pump_id", "devices", ["pump_id"])
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("company_id", sa.String(length=32), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id")),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_index("ix_users_station_id", "users", ["station_id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("pump_id", sa.String(length=32), sa.ForeignKey("pumps.id"), nullable=False),
        sa.Column("nozzle_id", sa.String(length=32), sa.ForeignKey("nozzles.id"), nullable=False),
        sa.Column("device_id", sa.String(length=32), sa.ForeignKey("devices.id")),
        sa.Column("attendant_id", sa.String(length=32), sa.ForeignKey("users.id")),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("liters", sa.Float(), nullable=False),
        sa.Column("price_per_liter", sa.Float(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("pulse_count", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_transactions_station_id", "transactions", ["station_id"])
    op.create_index("ix_transactions_pump_id", "transactions", ["pump_id"])
    op.create_index("ix_transactions_device_id", "transactions", ["device_id"])
    op.create_index("ix_transactions_attendant_id", "transactions", ["attendant_id"])
    op.create_index("ix_transactions_start_time", "transactions", ["start_time"])
    op.create_index("ix_transactions_end_time", "transactions", ["end_time"])
    op.create_table(
        "telemetry_logs",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("pump_id", sa.String(length=32), sa.ForeignKey("pumps.id"), nullable=False),
        sa.Column("device_id", sa.String(length=32), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("pulse_count", sa.Integer(), nullable=False),
        sa.Column("flowing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("voltage", sa.Float()),
        sa.Column("rssi", sa.Integer()),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_telemetry_logs_station_id", "telemetry_logs", ["station_id"])
    op.create_index("ix_telemetry_logs_pump_id", "telemetry_logs", ["pump_id"])
    op.create_index("ix_telemetry_logs_device_id", "telemetry_logs", ["device_id"])
    op.create_index("ix_telemetry_logs_timestamp", "telemetry_logs", ["timestamp"])
    op.create_index(
        "ix_telemetry_logs_station_pump_timestamp",
        "telemetry_logs",
        ["station_id", "pump_id", "timestamp"],
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("station_id", sa.String(length=32), sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("pump_id", sa.String(length=32), sa.ForeignKey("pumps.id")),
        sa.Column("device_id", sa.String(length=32), sa.ForeignKey("devices.id")),
        sa.Column("severity", alert_severity_enum, nullable=False),
        sa.Column("status", alert_status_enum, nullable=False, server_default="open"),
        sa.Column("rule_name", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("acknowledged_by", sa.String(length=32), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_alerts_station_id", "alerts", ["station_id"])
    op.create_index("ix_alerts_pump_id", "alerts", ["pump_id"])
    op.create_index("ix_alerts_device_id", "alerts", ["device_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("user_id", sa.String(length=32), sa.ForeignKey("users.id")),
        sa.Column("action", audit_action_enum, nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64)),
        sa.Column("details", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(length=64)),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_alerts_device_id", table_name="alerts")
    op.drop_index("ix_alerts_pump_id", table_name="alerts")
    op.drop_index("ix_alerts_station_id", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_telemetry_logs_station_pump_timestamp", table_name="telemetry_logs")
    op.drop_index("ix_telemetry_logs_timestamp", table_name="telemetry_logs")
    op.drop_index("ix_telemetry_logs_device_id", table_name="telemetry_logs")
    op.drop_index("ix_telemetry_logs_pump_id", table_name="telemetry_logs")
    op.drop_index("ix_telemetry_logs_station_id", table_name="telemetry_logs")
    op.drop_table("telemetry_logs")
    op.drop_index("ix_transactions_end_time", table_name="transactions")
    op.drop_index("ix_transactions_start_time", table_name="transactions")
    op.drop_index("ix_transactions_attendant_id", table_name="transactions")
    op.drop_index("ix_transactions_device_id", table_name="transactions")
    op.drop_index("ix_transactions_pump_id", table_name="transactions")
    op.drop_index("ix_transactions_station_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_station_id", table_name="users")
    op.drop_index("ix_users_company_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_devices_pump_id", table_name="devices")
    op.drop_index("ix_devices_station_id", table_name="devices")
    op.drop_table("devices")
    op.drop_index("ix_nozzles_pump_id", table_name="nozzles")
    op.drop_table("nozzles")
    op.drop_index("ix_pumps_station_id", table_name="pumps")
    op.drop_table("pumps")
    op.drop_index("ix_stations_company_id", table_name="stations")
    op.drop_table("stations")
    op.drop_table("companies")

    bind = op.get_bind()
    audit_action_enum.drop(bind, checkfirst=True)
    device_status_enum.drop(bind, checkfirst=True)
    alert_status_enum.drop(bind, checkfirst=True)
    alert_severity_enum.drop(bind, checkfirst=True)
    pump_status_enum.drop(bind, checkfirst=True)
    role_enum.drop(bind, checkfirst=True)
