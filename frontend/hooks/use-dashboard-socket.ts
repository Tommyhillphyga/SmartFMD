"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_BASE_URL?.replace(/\/$/, "") ?? "ws://localhost/api";
const LIVE_REFRESH_INTERVAL_MS = 2000;

export function useDashboardSocket(stationId?: string | null) {
  const queryClient = useQueryClient();
  const [latestEvent, setLatestEvent] = useState<string | null>(null);
  const refreshTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!stationId) {
      return;
    }

    const flushLiveQueries = () => {
      refreshTimerRef.current = null;
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] });
      void queryClient.invalidateQueries({ queryKey: ["stationDashboard", stationId] });
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["transactions"] });
      void queryClient.invalidateQueries({ queryKey: ["reportsOverview"] });
      void queryClient.invalidateQueries({ queryKey: ["devices"] });
    };

    const scheduleRefresh = () => {
      if (refreshTimerRef.current !== null) {
        return;
      }
      refreshTimerRef.current = window.setTimeout(flushLiveQueries, LIVE_REFRESH_INTERVAL_MS);
    };

    const socket = new WebSocket(`${WS_BASE_URL}/ws/dashboard/${stationId}`);
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLatestEvent(message.event);
      scheduleRefresh();
    };
    socket.onerror = () => setLatestEvent("socket_error");

    return () => {
      if (refreshTimerRef.current !== null) {
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
      socket.close();
    };
  }, [queryClient, stationId]);

  return latestEvent;
}
