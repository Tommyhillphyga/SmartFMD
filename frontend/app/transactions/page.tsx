"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/dashboard/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableHeaderRow, TableRow } from "@/components/ui/table";
import { exportsApi, api } from "@/lib/api";
import { triggerDownload } from "@/lib/export";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

export default function TransactionsPage() {
  const accessToken = useAuthStore((state) => state.accessToken);
  const transactionsQuery = useQuery({
    queryKey: ["transactions"],
    queryFn: () => api.transactions(new URLSearchParams({ limit: "100" })),
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-primary">Transactions</p>
            <h1 className="mt-3 text-5xl">Fuel sales ledger</h1>
          </div>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => triggerDownload(exportsApi.csv, accessToken, "transactions.csv")}
            >
              Export CSV
            </Button>
            <Button onClick={() => triggerDownload(exportsApi.pdf, accessToken, "analytics-summary.pdf")}>
              Export PDF
            </Button>
          </div>
        </div>

        <Card>
          <CardTitle>Completed transactions</CardTitle>
          <CardDescription className="mt-2">Last 100 fueling events stored by the platform.</CardDescription>
          <div className="mt-5 overflow-x-auto">
            <Table>
              <TableHead>
                <TableHeaderRow>
                  <TableHeader>ID</TableHeader>
                  <TableHeader>Pump</TableHeader>
                  <TableHeader>Attendant</TableHeader>
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
                    <TableCell>{transaction.pump_id}</TableCell>
                    <TableCell>{transaction.attendant_id ?? "Unassigned"}</TableCell>
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

