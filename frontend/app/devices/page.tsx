"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/dashboard/app-shell";
import { DeviceHealthTable } from "@/components/dashboard/device-health-table";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function DevicesPage() {
  const devicesQuery = useQuery({
    queryKey: ["devices"],
    queryFn: () => api.devices(),
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Device Management</p>
          <h1 className="mt-3 text-5xl">Retrofitted controller fleet</h1>
        </div>
        <Card>
          <CardTitle>Device estate</CardTitle>
          <CardDescription className="mt-2">Monitor firmware, signal health, and heartbeat freshness for every device.</CardDescription>
        </Card>
        <DeviceHealthTable devices={devicesQuery.data ?? []} />
      </div>
    </AppShell>
  );
}

