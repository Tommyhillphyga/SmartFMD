"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AppShell } from "@/components/dashboard/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableHeaderRow, TableRow } from "@/components/ui/table";
import { api } from "@/lib/api";
import { severityTone } from "@/lib/utils";

export default function AlertsPage() {
  const queryClient = useQueryClient();
  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.alerts(new URLSearchParams({ status: "open" })),
  });
  const acknowledgeMutation = useMutation({
    mutationFn: api.acknowledgeAlert,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Alerts Center</p>
          <h1 className="mt-3 text-5xl">Fraud and anomaly queue</h1>
        </div>

        <Card>
          <CardTitle>Open alerts</CardTitle>
          <CardDescription className="mt-2">Acknowledge alerts once they have been reviewed by operations.</CardDescription>
          <div className="mt-5 overflow-x-auto">
            <Table>
              <TableHead>
                <TableHeaderRow>
                  <TableHeader>Severity</TableHeader>
                  <TableHeader>Rule</TableHeader>
                  <TableHeader>Message</TableHeader>
                  <TableHeader>Created</TableHeader>
                  <TableHeader />
                </TableHeaderRow>
              </TableHead>
              <TableBody>
                {(alertsQuery.data ?? []).map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${severityTone(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </TableCell>
                    <TableCell>{alert.rule_name}</TableCell>
                    <TableCell>{alert.message}</TableCell>
                    <TableCell>{new Date(alert.created_at).toLocaleString()}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => acknowledgeMutation.mutate(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="mt-4">
            <Badge variant="warning">{alertsQuery.data?.length ?? 0} items in queue</Badge>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

