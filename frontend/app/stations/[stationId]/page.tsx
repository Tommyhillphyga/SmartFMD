"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { RevenueAreaChart } from "@/components/charts/revenue-area-chart";
import { AlertStream } from "@/components/dashboard/alert-stream";
import { AppShell } from "@/components/dashboard/app-shell";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { PumpGrid } from "@/components/dashboard/pump-grid";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { useDashboardSocket } from "@/hooks/use-dashboard-socket";

export default function StationDetailPage() {
  const params = useParams<{ stationId: string }>();
  const stationId = params.stationId;
  const stationQuery = useQuery({
    queryKey: ["stationDashboard", stationId],
    queryFn: () => api.stationDetail(stationId),
  });
  const alertsQuery = useQuery({
    queryKey: ["alerts", stationId],
    queryFn: () => api.alerts(new URLSearchParams({ station_id: stationId, status: "open" })),
  });
  const reportsQuery = useQuery({
    queryKey: ["reportsOverview", stationId],
    queryFn: () => api.reportsOverview(stationId),
  });
  const latestEvent = useDashboardSocket(stationId);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-primary">Station Detail</p>
            <h1 className="mt-3 text-5xl">{stationQuery.data?.station.name ?? stationId}</h1>
            <p className="mt-3 text-foreground/65">{stationQuery.data?.station.location}</p>
          </div>
          <div className="rounded-full border border-success/30 bg-success/10 px-4 py-2 text-sm text-success">
            Last live event: {latestEvent ?? "listening"}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Active sessions"
            value={String(stationQuery.data?.active_sessions ?? 0)}
            caption="Pumps dispensing right now at this station."
          />
          <KpiCard
            label="Liters today"
            value={formatNumber(stationQuery.data?.liters_today ?? 0)}
            caption="Daily station throughput."
          />
          <KpiCard
            label="Revenue today"
            value={formatCurrency(stationQuery.data?.revenue_today ?? 0)}
            caption="Gross revenue for this station today."
          />
          <KpiCard
            label="Alerts open"
            value={String(stationQuery.data?.alerts_open ?? 0)}
            caption="Exceptions requiring manager attention."
          />
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
          <RevenueAreaChart
            data={reportsQuery.data?.daily_revenue ?? []}
            title="Station revenue"
            description="Daily revenue for the selected station."
            dataKey="revenue"
          />
          <AlertStream alerts={alertsQuery.data ?? []} />
        </div>

        <PumpGrid pumps={stationQuery.data?.pumps ?? []} />
      </div>
    </AppShell>
  );
}

