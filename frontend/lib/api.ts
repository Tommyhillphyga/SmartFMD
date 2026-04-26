"use client";

import type {
  Alert,
  AuthResponse,
  DashboardOverview,
  Device,
  PumpDetail,
  ReportSummary,
  Station,
  StationDashboard,
  Transaction,
  User,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost/api";

function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("sfmd_access_token");
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { authenticated?: boolean },
): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");

  if (init?.authenticated !== false) {
    const token = getAccessToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  if (response.headers.get("content-type")?.includes("application/json")) {
    return response.json() as Promise<T>;
  }

  return (await response.blob()) as T;
}

export const api = {
  login: (payload: { email: string; password: string }) =>
    apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      authenticated: false,
      body: JSON.stringify(payload),
    }),
  refresh: (refreshToken: string) =>
    apiFetch<AuthResponse>("/auth/refresh", {
      method: "POST",
      authenticated: false,
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
  me: () => apiFetch<User>("/auth/me"),
  stations: () => apiFetch<Station[]>("/stations"),
  dashboardOverview: () => apiFetch<DashboardOverview>("/stations/dashboard/overview"),
  stationDetail: (stationId: string) => apiFetch<StationDashboard>(`/stations/${stationId}`),
  pumpDetail: (pumpId: string) => apiFetch<PumpDetail>(`/pumps/${pumpId}`),
  alerts: (params?: URLSearchParams) =>
    apiFetch<Alert[]>(`/alerts${params ? `?${params.toString()}` : ""}`),
  acknowledgeAlert: (alertId: string) =>
    apiFetch<{ message: string }>(`/alerts/${alertId}/acknowledge`, {
      method: "POST",
      body: JSON.stringify({}),
    }),
  transactions: (params?: URLSearchParams) =>
    apiFetch<Transaction[]>(`/transactions${params ? `?${params.toString()}` : ""}`),
  reportsOverview: (stationId?: string) =>
    apiFetch<ReportSummary>(`/reports/overview${stationId ? `?station_id=${stationId}` : ""}`),
  devices: (stationId?: string) =>
    apiFetch<Device[]>(`/devices${stationId ? `?station_id=${stationId}` : ""}`),
};

export const exportsApi = {
  csv: `${API_BASE_URL}/reports/export/csv`,
  pdf: `${API_BASE_URL}/reports/export/pdf`,
};

