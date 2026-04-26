import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { severityTone } from "@/lib/utils";
import type { Alert } from "@/types/api";

export function AlertStream({ alerts }: { alerts: Alert[] }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <CardTitle>Alert Stream</CardTitle>
          <CardDescription>Realtime fraud and health alerts across active stations.</CardDescription>
        </div>
        <Badge variant="warning">{alerts.length} open</Badge>
      </div>
      <div className="mt-5 space-y-3">
        {alerts.length === 0 ? (
          <p className="text-sm text-foreground/55">No active alerts right now.</p>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="rounded-xl border border-border/70 bg-background/40 p-4 text-sm"
            >
              <div className="flex items-center justify-between gap-3">
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${severityTone(alert.severity)}`}>
                  {alert.severity}
                </span>
                <span className="text-foreground/45">{new Date(alert.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-3 font-semibold">{alert.rule_name.replaceAll("_", " ")}</p>
              <p className="mt-1 text-foreground/65">{alert.message}</p>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}

