"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect } from "react";

import { ComparisonBarChart } from "@/components/charts/comparison-bar-chart";
import { RevenueAreaChart } from "@/components/charts/revenue-area-chart";
import { AlertStream } from "@/components/dashboard/alert-stream";
import { AppShell } from "@/components/dashboard/app-shell";
import { DeviceHealthTable } from "@/components/dashboard/device-health-table";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { SessionsTicker } from "@/components/dashboard/sessions-ticker";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { useDashboardSocket } from "@/hooks/use-dashboard-socket";
import { useUiStore } from "@/store/ui-store";

export default function DashboardPage() {
  const activeStationId = useUiStore((state) => state.activeStationId);
  const setActiveStationId = useUiStore((state) => state.setActiveStationId);
  const overviewQuery = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: api.dashboardOverview,
  });
  const reportQuery = useQuery({
    queryKey: ["reportsOverview"],
    queryFn: () => api.reportsOverview(),
  });
  const transactionsQuery = useQuery({
    queryKey: ["transactions", "recent"],
    queryFn: () => api.transactions(new URLSearchParams({ limit: "12" })),
  });
  const devicesQuery = useQuery({
    queryKey: ["devices"],
    queryFn: () => api.devices(),
  });

  const socketStationId = activeStationId ?? overviewQuery.data?.stations[0]?.id;
  const latestEvent = useDashboardSocket(socketStationId);

  useEffect(() => {
    if (overviewQuery.data?.stations[0] && !activeStationId) {
      setActiveStationId(overviewQuery.data.stations[0].id);
    }
  }, [activeStationId, overviewQuery.data?.stations, setActiveStationId]);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-primary">Overview</p>
            <h1 className="mt-3 text-5xl">Forecourt pulse at a glance</h1>
            <p className="mt-3 max-w-2xl text-foreground/65">
              Live view of active dispensing, revenue accumulation, alert posture, and device health across
              the connected estate.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-success/30 bg-success/10 px-4 py-2 text-sm text-success">
              Live websocket: {latestEvent ?? "connected"}
            </div>
            <Button asChild variant="secondary">
              <Link href="/analytics">Deep analytics</Link>
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Active fueling sessions"
            value={String(overviewQuery.data?.active_sessions ?? 0)}
            caption="Pumps currently dispensing in realtime."
          />
          <KpiCard
            label="Liters sold today"
            value={formatNumber(overviewQuery.data?.liters_today ?? 0)}
            caption="Cumulative liters from completed transactions."
          />
          <KpiCard
            label="Revenue today"
            value={formatCurrency(overviewQuery.data?.revenue_today ?? 0)}
            caption="Gross value of today’s dispensed fuel."
          />
          <KpiCard
            label="Open alerts"
            value={String(overviewQuery.data?.open_alerts ?? 0)}
            caption="Fraud, tamper, and operational exceptions."
          />
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
          <RevenueAreaChart
            data={overviewQuery.data?.trends ?? []}
            title="Revenue trend"
            description="Daily revenue progression for the trailing window."
            dataKey="revenue"
          />
          <AlertStream alerts={overviewQuery.data?.recent_alerts ?? []} />
        </div>

        <SessionsTicker transactions={transactionsQuery.data ?? []} />

        <div className="grid gap-6 xl:grid-cols-2">
          <ComparisonBarChart
            data={reportQuery.data?.station_ranking ?? []}
            title="Station ranking"
            description="Revenue leaderboard across monitored sites."
            dataKey="revenue"
          />
          <Card>
            <CardTitle>Station focus</CardTitle>
            <CardDescription className="mt-2">
              Jump directly into a station live board to inspect pump health and session activity.
            </CardDescription>
            <div className="mt-5 grid gap-3">
              {(overviewQuery.data?.stations ?? []).map((station) => (
                <Link
                  key={station.id}
                  href={`/stations/${station.id}`}
                  className="rounded-xl border border-border/60 bg-background/50 p-4 transition hover:border-primary/50"
                >
                  <p className="font-semibold">{station.name}</p>
                  <p className="mt-1 text-sm text-foreground/55">
                    {station.location}, {station.city}
                  </p>
                </Link>
              ))}
            </div>
          </Card>
        </div>

        <DeviceHealthTable devices={devicesQuery.data ?? []} />
      </div>
    </AppShell>
  );
}
