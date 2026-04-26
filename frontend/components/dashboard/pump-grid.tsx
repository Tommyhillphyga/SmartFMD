import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatNumber } from "@/lib/utils";
import type { PumpSnapshot } from "@/types/api";

const statusVariant: Record<string, "success" | "warning" | "danger" | "info" | "neutral"> = {
  fueling: "success",
  idle: "neutral",
  offline: "warning",
  tampered: "danger",
  error: "danger",
};

export function PumpGrid({ pumps }: { pumps: PumpSnapshot[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {pumps.map((pump) => (
        <Link href={`/pumps/${pump.id}`} key={pump.id}>
          <Card className="h-full transition hover:-translate-y-1 hover:border-primary/60">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{pump.name}</CardTitle>
                <CardDescription>{pump.id}</CardDescription>
              </div>
              <Badge variant={statusVariant[pump.status] ?? "neutral"}>{pump.status}</Badge>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-foreground/45">Liters today</p>
                <p className="mt-1 text-xl font-semibold">{formatNumber(pump.liters_today)}</p>
              </div>
              <div>
                <p className="text-foreground/45">Revenue today</p>
                <p className="mt-1 text-xl font-semibold">{formatCurrency(pump.revenue_today)}</p>
              </div>
              <div>
                <p className="text-foreground/45">Pulse count</p>
                <p className="mt-1 font-medium">{pump.current_pulse_count ?? "N/A"}</p>
              </div>
              <div>
                <p className="text-foreground/45">Device</p>
                <p className="mt-1 font-medium">{pump.device_id ?? "Unpaired"}</p>
              </div>
            </div>
          </Card>
        </Link>
      ))}
    </div>
  );
}

