"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_BASE_URL?.replace(/\/$/, "") ?? "ws://localhost/api";

export function useDashboardSocket(stationId?: string | null) {
  const queryClient = useQueryClient();
  const [latestEvent, setLatestEvent] = useState<string | null>(null);

  useEffect(() => {
    if (!stationId) {
      return;
    }

    const socket = new WebSocket(`${WS_BASE_URL}/ws/dashboard/${stationId}`);
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLatestEvent(message.event);
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] });
      void queryClient.invalidateQueries({ queryKey: ["stationDashboard", stationId] });
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["transactions"] });
      void queryClient.invalidateQueries({ queryKey: ["reportsOverview"] });
    };
    socket.onerror = () => setLatestEvent("socket_error");

    return () => {
      socket.close();
    };
  }, [queryClient, stationId]);

  return latestEvent;
}

