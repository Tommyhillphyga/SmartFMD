"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

type ThemeMode = "light" | "dark";

interface UiState {
  theme: ThemeMode;
  activeStationId: string | null;
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
  setActiveStationId: (stationId: string | null) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set, get) => ({
      theme: "dark",
      activeStationId: null,
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set({ theme: get().theme === "dark" ? "light" : "dark" }),
      setActiveStationId: (activeStationId) => set({ activeStationId }),
    }),
    {
      name: "smartfmd-ui",
    },
  ),
);

