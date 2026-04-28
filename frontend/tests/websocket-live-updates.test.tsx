import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render } from "@testing-library/react";
import { useEffect } from "react";
import { vi } from "vitest";

import { useDashboardSocket } from "@/hooks/use-dashboard-socket";

class MockSocket {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: (() => void) | null = null;

  constructor() {
    setTimeout(() => {
      this.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({ event: "telemetry", pump_id: "PUMP01" }),
        }),
      );
    }, 0);
  }

  close() {}
}

describe("useDashboardSocket", () => {
  it("invalidates live queries when a websocket event arrives", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", MockSocket as unknown as typeof WebSocket);
    const queryClient = new QueryClient();
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

    function TestComponent() {
      useDashboardSocket("STA001");
      useEffect(() => {}, []);
      return null;
    }

    render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>,
    );

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(invalidateSpy).toHaveBeenCalled();

    vi.useRealTimers();
  });
});
