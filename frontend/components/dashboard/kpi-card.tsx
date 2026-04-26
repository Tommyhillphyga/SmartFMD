import { ArrowUpRight } from "lucide-react";

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function KpiCard({
  label,
  value,
  caption,
}: {
  label: string;
  value: string;
  caption: string;
}) {
  return (
    <Card className="animate-slide-up bg-gradient-to-br from-card via-card to-muted/35">
      <CardHeader className="mb-2">
        <div>
          <CardDescription>{label}</CardDescription>
          <CardTitle className="mt-2 text-3xl">{value}</CardTitle>
        </div>
        <div className="rounded-full bg-primary/10 p-2 text-primary">
          <ArrowUpRight className="h-4 w-4" />
        </div>
      </CardHeader>
      <p className="text-sm text-foreground/55">{caption}</p>
    </Card>
  );
}

