export type Role =
  | "super_admin"
  | "station_owner"
  | "manager"
  | "attendant"
  | "auditor";

export type PumpStatus = "idle" | "fueling" | "offline" | "tampered" | "error";
export type AlertSeverity = "low" | "medium" | "critical";
export type AlertStatus = "open" | "acknowledged" | "resolved";
export type DeviceStatus = "online" | "offline" | "degraded";

export interface User {
  id: string;
  company_id: string;
  station_id: string | null;
  full_name: string;
  email: string;
  role: Role;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Station {
  id: string;
  company_id: string;
  name: string;
  location: string;
  city: string;
  timezone: string;
}

export interface PumpSnapshot {
  id: string;
  name: string;
  status: PumpStatus;
  liters_today: number;
  revenue_today: number;
  current_pulse_count: number | null;
  device_id: string | null;
  last_seen: string | null;
}

export interface DashboardOverview {
  active_sessions: number;
  liters_today: number;
  revenue_today: number;
  open_alerts: number;
  stations: Station[];
  recent_alerts: Alert[];
  trends: TrendPoint[];
}

export interface StationDashboard {
  station: Station;
  pumps: PumpSnapshot[];
  active_sessions: number;
  liters_today: number;
  revenue_today: number;
  alerts_open: number;
  transaction_count_today: number;
}

export interface PumpDetail {
  id: string;
  station_id: string;
  name: string;
  status: PumpStatus;
  product_name: string;
  totalizer_liters: number;
  totalizer_amount: number;
  latest_telemetry: Record<string, unknown> | null;
  active_transactions: Record<string, unknown>[];
  device: Record<string, unknown> | null;
}

export interface Alert {
  id: string;
  station_id: string;
  pump_id: string | null;
  device_id: string | null;
  severity: AlertSeverity;
  status: AlertStatus;
  rule_name: string;
  message: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
}

export interface Transaction {
  id: string;
  station_id: string;
  pump_id: string;
  nozzle_id: string;
  device_id: string | null;
  attendant_id: string | null;
  start_time: string;
  end_time: string;
  liters: number;
  price_per_liter: number;
  amount: number;
  pulse_count: number;
  duration_seconds: number;
  metadata_json: Record<string, unknown>;
}

export interface TrendPoint {
  label: string;
  liters?: number;
  revenue?: number;
  alerts?: number;
}

export interface ReportSummary {
  daily_liters_sold: TrendPoint[];
  daily_revenue: TrendPoint[];
  pump_comparison: { pump_id: string; name: string; liters: number; revenue: number }[];
  station_ranking: { station_id: string; name: string; revenue: number }[];
  anomaly_trends: TrendPoint[];
  attendant_productivity: {
    attendant_id: string;
    name: string;
    transactions: number;
    revenue: number;
  }[];
}

export interface Device {
  id: string;
  station_id: string;
  pump_id: string;
  firmware_version: string;
  status: DeviceStatus;
  last_heartbeat: string | null;
  rssi: number | null;
  voltage: number | null;
  battery_level: number | null;
  metadata_json: Record<string, unknown>;
}

