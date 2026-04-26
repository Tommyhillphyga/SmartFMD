import { render, screen } from "@testing-library/react";

import { RevenueAreaChart } from "@/components/charts/revenue-area-chart";

describe("RevenueAreaChart", () => {
  it("renders chart metadata", () => {
    render(
      <RevenueAreaChart
        title="Revenue trend"
        description="Daily revenue progression"
        dataKey="revenue"
        data={[
          { label: "2026-04-20", revenue: 1000 },
          { label: "2026-04-21", revenue: 1200 },
        ]}
      />,
    );

    expect(screen.getByText("Revenue trend")).toBeInTheDocument();
    expect(screen.getByText("Daily revenue progression")).toBeInTheDocument();
  });
});

