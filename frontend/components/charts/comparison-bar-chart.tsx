"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export function ComparisonBarChart({
  data,
  title,
  description,
  dataKey,
}: {
  data: Array<Record<string, string | number>>;
  title: string;
  description: string;
  dataKey: string;
}) {
  return (
    <Card className="h-full">
      <div className="mb-4">
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" vertical={false} />
            <XAxis dataKey="name" stroke="rgba(148,163,184,0.6)" fontSize={12} />
            <YAxis stroke="rgba(148,163,184,0.6)" fontSize={12} />
            <Tooltip />
            <Bar dataKey={dataKey} fill="#0cb05a" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

