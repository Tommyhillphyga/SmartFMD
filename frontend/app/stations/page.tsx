"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { AppShell } from "@/components/dashboard/app-shell";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function StationsPage() {
  const stationsQuery = useQuery({
    queryKey: ["stations"],
    queryFn: api.stations,
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Stations</p>
          <h1 className="mt-3 text-5xl">Multi-station command board</h1>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {(stationsQuery.data ?? []).map((station) => (
            <Link key={station.id} href={`/stations/${station.id}`}>
              <Card className="h-full transition hover:-translate-y-1 hover:border-primary/50">
                <CardTitle>{station.name}</CardTitle>
                <CardDescription className="mt-2">
                  {station.location}, {station.city}
                </CardDescription>
                <p className="mt-5 text-sm text-foreground/55">{station.id}</p>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  );
}

