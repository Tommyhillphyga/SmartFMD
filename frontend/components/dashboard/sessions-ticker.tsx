import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatNumber } from "@/lib/utils";
import type { Transaction } from "@/types/api";

export function SessionsTicker({ transactions }: { transactions: Transaction[] }) {
  const items = [...transactions, ...transactions];

  return (
    <Card className="overflow-hidden">
      <div className="mb-4">
        <CardTitle>Fueling Session Ticker</CardTitle>
        <CardDescription>Recent completed sessions rolling across all monitored stations.</CardDescription>
      </div>
      <div className="overflow-hidden">
        <div className="flex min-w-max animate-ticker gap-3">
          {items.map((transaction, index) => (
            <div
              key={`${transaction.id}-${index}`}
              className="min-w-[240px] rounded-xl border border-border/60 bg-background/55 px-4 py-3 text-sm"
            >
              <p className="font-semibold">{transaction.pump_id}</p>
              <p className="mt-1 text-foreground/60">
                {formatNumber(transaction.liters)} L • {formatCurrency(transaction.amount)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

