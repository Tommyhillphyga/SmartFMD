import { expect, test } from "@playwright/test";

test("login, receive live update, surface anomaly, and export report", async ({ page }) => {
  const state = {
    alertTriggered: false,
  };

  await page.exposeFunction("notifyAlertTriggered", () => {
    state.alertTriggered = true;
  });

  await page.addInitScript(() => {
    class MockWebSocket {
      url: string;
      onopen: ((event: Event) => void) | null = null;
      onmessage: ((event: MessageEvent) => void) | null = null;
      onerror: ((event: Event) => void) | null = null;

      constructor(url: string) {
        this.url = url;
        setTimeout(() => {
          this.onopen?.(new Event("open"));
          this.onmessage?.(
            new MessageEvent("message", {
              data: JSON.stringify({ event: "telemetry", station_id: "STA001" }),
            }),
          );
          setTimeout(() => {
            (window as Window & { notifyAlertTriggered: () => void }).notifyAlertTriggered();
            this.onmessage?.(
              new MessageEvent("message", {
                data: JSON.stringify({ event: "alert", station_id: "STA001" }),
              }),
            );
          }, 300);
        }, 100);
      }

      send() {}
      close() {}
      addEventListener() {}
      removeEventListener() {}
    }

    // @ts-expect-error test shim
    window.WebSocket = MockWebSocket;
  });

  await page.route("**/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "token",
        refresh_token: "refresh",
        token_type: "bearer",
        user: {
          id: "USRADMIN",
          company_id: "COM001",
          station_id: null,
          full_name: "Admin User",
          email: "admin@example.com",
          role: "super_admin",
          is_active: true,
        },
      }),
    });
  });

  await page.route("**/stations/dashboard/overview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        active_sessions: 2,
        liters_today: 1204.5,
        revenue_today: 1184000,
        open_alerts: state.alertTriggered ? 1 : 0,
        stations: [
          {
            id: "STA001",
            company_id: "COM001",
            name: "Lekki Phase 1 Station",
            location: "Admiralty Way, Lekki",
            city: "Lagos",
            timezone: "Africa/Lagos",
          },
        ],
        recent_alerts: state.alertTriggered
          ? [
              {
                id: "ALT001",
                station_id: "STA001",
                pump_id: "PUMP01",
                device_id: "DEV001",
                severity: "critical",
                status: "open",
                rule_name: "abnormally_low_pulses_per_liter",
                message: "Observed pulses per liter are materially below the expected calibration range.",
                metadata_json: {},
                created_at: "2026-04-24T11:01:02Z",
                acknowledged_at: null,
                acknowledged_by: null,
              },
            ]
          : [],
        trends: [
          { label: "2026-04-22", liters: 500, revenue: 450000, alerts: 0 },
          { label: "2026-04-23", liters: 700, revenue: 680000, alerts: 1 },
        ],
      }),
    });
  });

  await page.route("**/reports/overview", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        daily_liters_sold: [
          { label: "2026-04-22", liters: 500 },
          { label: "2026-04-23", liters: 700 },
        ],
        daily_revenue: [
          { label: "2026-04-22", revenue: 450000 },
          { label: "2026-04-23", revenue: 680000 },
        ],
        pump_comparison: [{ pump_id: "PUMP01", name: "Pump 01", liters: 700, revenue: 680000 }],
        station_ranking: [{ station_id: "STA001", name: "Lekki Phase 1 Station", revenue: 680000 }],
        anomaly_trends: [{ label: "2026-04-23", alerts: state.alertTriggered ? 1 : 0 }],
        attendant_productivity: [
          { attendant_id: "ATT001", name: "Attendant 1", transactions: 4, revenue: 120000 },
        ],
      }),
    });
  });

  await page.route("**/transactions?limit=12", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: "TXN001",
          station_id: "STA001",
          pump_id: "PUMP01",
          nozzle_id: "NOZ01",
          device_id: "DEV001",
          attendant_id: "ATT001",
          start_time: "2026-04-24T11:00:00Z",
          end_time: "2026-04-24T11:01:02Z",
          liters: 12.35,
          price_per_liter: 972,
          amount: 12000,
          pulse_count: 1235,
          duration_seconds: 55,
          metadata_json: {},
        },
      ]),
    });
  });

  await page.route("**/devices", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: "DEV001",
          station_id: "STA001",
          pump_id: "PUMP01",
          firmware_version: "1.0.0",
          status: "online",
          last_heartbeat: "2026-04-24T11:00:59Z",
          rssi: -65,
          voltage: 12.1,
          battery_level: null,
          metadata_json: {},
        },
      ]),
    });
  });

  await page.route("**/alerts?status=open", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        state.alertTriggered
          ? [
              {
                id: "ALT001",
                station_id: "STA001",
                pump_id: "PUMP01",
                device_id: "DEV001",
                severity: "critical",
                status: "open",
                rule_name: "abnormally_low_pulses_per_liter",
                message: "Observed pulses per liter are materially below the expected calibration range.",
                metadata_json: {},
                created_at: "2026-04-24T11:01:02Z",
                acknowledged_at: null,
                acknowledged_by: null,
              },
            ]
          : [],
      ),
    });
  });

  await page.route("**/reports/export/pdf", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/pdf",
      body: "%PDF-1.4 test",
      headers: {
        "Content-Disposition": "attachment; filename=analytics-summary.pdf",
      },
    });
  });

  await page.goto("/login");
  await page.getByRole("button", { name: /access dashboard/i }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByText("Forecourt pulse at a glance")).toBeVisible();
  await expect(page.getByText(/Live websocket: telemetry/i)).toBeVisible();
  await expect(page.getByText(/abnormally low pulses per liter/i)).toBeVisible();

  await page.goto("/transactions");
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: /export pdf/i }).click(),
  ]);
  expect(await download.suggestedFilename()).toContain("analytics-summary.pdf");
});
