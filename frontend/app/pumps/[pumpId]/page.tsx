"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { AppShell } from "@/components/dashboard/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableHeaderRow, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";

export default function PumpDetailPage() {
  const params = useParams<{ pumpId: string }>();
  const pumpId = params.pumpId;
  const pumpQuery = useQuery({
    queryKey: ["pumpDetail", pumpId],
    queryFn: () => api.pumpDetail(pumpId),
  });
  const transactionsQuery = useQuery({
    queryKey: ["transactions", pumpId],
    queryFn: () => api.transactions(new URLSearchParams({ pump_id: pumpId, limit: "20" })),
  });

  const pump = pumpQuery.data;

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-primary">Pump Detail</p>
            <h1 className="mt-3 text-5xl">{pump?.name ?? pumpId}</h1>
            <p className="mt-3 text-foreground/65">Live telemetry and transaction audit trail for the selected pump.</p>
          </div>
          <Badge variant={pump?.status === "fueling" ? "success" : "neutral"}>{pump?.status ?? "loading"}</Badge>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardTitle>Realtime telemetry</CardTitle>
            <CardDescription className="mt-2">Most recent heartbeat from the retrofitted ESP32 pulse reader.</CardDescription>
            <div className="mt-5 space-y-3 text-sm">
              <p>Pulse count: {String(pump?.latest_telemetry?.pulse_count ?? "N/A")}</p>
              <p>Flowing: {String(pump?.latest_telemetry?.flowing ?? false)}</p>
              <p>Voltage: {String(pump?.latest_telemetry?.voltage ?? "N/A")} V</p>
              <p>RSSI: {String(pump?.latest_telemetry?.rssi ?? "N/A")} dBm</p>
            </div>
          </Card>
          <Card>
            <CardTitle>Totalizers</CardTitle>
            <CardDescription className="mt-2">Cumulative throughput from persisted transactions.</CardDescription>
            <div className="mt-5 space-y-3 text-sm">
              <p>Liters: {formatNumber(pump?.totalizer_liters ?? 0)}</p>
              <p>Revenue: {formatCurrency(pump?.totalizer_amount ?? 0)}</p>
              <p>Product: {pump?.product_name ?? "PMS"}</p>
              <p>Device: {String(pump?.device?.id ?? "Unpaired")}</p>
            </div>
          </Card>
          <Card>
            <CardTitle>Live session state</CardTitle>
            <CardDescription className="mt-2">Immediate view of whether this pump is actively fueling.</CardDescription>
            <div className="mt-5 text-sm">
              {pump?.active_transactions?.length ? (
                <p className="text-success">Fueling session active on this pump.</p>
              ) : (
                <p className="text-foreground/55">No active fueling session right now.</p>
              )}
            </div>
          </Card>
        </div>

        <Card>
          <CardTitle>Recent transactions</CardTitle>
          <CardDescription className="mt-2">Latest completed sales tied to this pump.</CardDescription>
          <div className="mt-5 overflow-x-auto">
            <Table>
              <TableHead>
                <TableHeaderRow>
                  <TableHeader>Transaction</TableHeader>
                  <TableHeader>Liters</TableHeader>
                  <TableHeader>Amount</TableHeader>
                  <TableHeader>Pulses</TableHeader>
                  <TableHeader>Duration</TableHeader>
                </TableHeaderRow>
              </TableHead>
              <TableBody>
                {(transactionsQuery.data ?? []).map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell>{transaction.id}</TableCell>
                    <TableCell>{formatNumber(transaction.liters)}</TableCell>
                    <TableCell>{formatCurrency(transaction.amount)}</TableCell>
                    <TableCell>{transaction.pulse_count}</TableCell>
                    <TableCell>{transaction.duration_seconds}s</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

