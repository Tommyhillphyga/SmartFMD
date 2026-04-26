"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import type { TrendPoint } from "@/types/api";

export function RevenueAreaChart({
  data,
  title,
  description,
  dataKey,
  stroke = "#00b08b",
}: {
  data: TrendPoint[];
  title: string;
  description: string;
  dataKey: "revenue" | "liters" | "alerts";
  stroke?: string;
}) {
  return (
    <Card className="h-full">
      <div className="mb-4">
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`fill-${dataKey}`} x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor={stroke} stopOpacity={0.45} />
                <stop offset="95%" stopColor={stroke} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" vertical={false} />
            <XAxis dataKey="label" stroke="rgba(148,163,184,0.6)" fontSize={12} />
            <YAxis stroke="rgba(148,163,184,0.6)" fontSize={12} />
            <Tooltip />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={stroke}
              fill={`url(#fill-${dataKey})`}
              strokeWidth={2.5}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

