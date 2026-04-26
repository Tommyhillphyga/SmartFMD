"use client";

import { useQuery } from "@tanstack/react-query";

import { ComparisonBarChart } from "@/components/charts/comparison-bar-chart";
import { RevenueAreaChart } from "@/components/charts/revenue-area-chart";
import { AppShell } from "@/components/dashboard/app-shell";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableHeaderRow, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";

export default function AnalyticsPage() {
  const reportQuery = useQuery({
    queryKey: ["reportsOverview"],
    queryFn: () => api.reportsOverview(),
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Analytics</p>
          <h1 className="mt-3 text-5xl">Performance, trends, and ranking</h1>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <RevenueAreaChart
            data={reportQuery.data?.daily_liters_sold ?? []}
            title="Daily liters sold"
            description="Volume throughput over the trailing window."
            dataKey="liters"
          />
          <RevenueAreaChart
            data={reportQuery.data?.anomaly_trends ?? []}
            title="Anomaly trend"
            description="Daily alert counts driven by the fraud engine."
            dataKey="alerts"
            stroke="#f59e0b"
          />
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <ComparisonBarChart
            data={reportQuery.data?.pump_comparison ?? []}
            title="Pump comparison"
            description="Revenue contribution by pump."
            dataKey="revenue"
          />
          <ComparisonBarChart
            data={reportQuery.data?.station_ranking ?? []}
            title="Station ranking"
            description="Revenue leaderboard by station."
            dataKey="revenue"
          />
        </div>

        <Card>
          <CardTitle>Attendant productivity</CardTitle>
          <CardDescription className="mt-2">Sales and throughput ranking by attendant.</CardDescription>
          <div className="mt-5 overflow-x-auto">
            <Table>
              <TableHead>
                <TableHeaderRow>
                  <TableHeader>Attendant</TableHeader>
                  <TableHeader>Transactions</TableHeader>
                  <TableHeader>Revenue</TableHeader>
                </TableHeaderRow>
              </TableHead>
              <TableBody>
                {(reportQuery.data?.attendant_productivity ?? []).slice(0, 15).map((attendant) => (
                  <TableRow key={attendant.attendant_id}>
                    <TableCell>{attendant.name}</TableCell>
                    <TableCell>{attendant.transactions}</TableCell>
                    <TableCell>{formatCurrency(attendant.revenue)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        <Card>
          <CardTitle>Daily revenue table</CardTitle>
          <CardDescription className="mt-2">Fast tabular reference for finance and audit workflows.</CardDescription>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {(reportQuery.data?.daily_revenue ?? []).map((point) => (
              <div key={point.label} className="rounded-xl border border-border/60 bg-background/50 p-4">
                <p className="text-sm text-foreground/55">{point.label}</p>
                <p className="mt-2 text-xl font-semibold">{formatCurrency(point.revenue ?? 0)}</p>
                <p className="mt-1 text-sm text-foreground/45">{formatNumber(point.liters ?? 0)} liters</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

