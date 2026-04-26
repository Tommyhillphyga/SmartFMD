"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/types/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setSession: (payload: {
    user: User;
    accessToken: string;
    refreshToken: string;
  }) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setSession: ({ user, accessToken, refreshToken }) => {
        if (typeof window !== "undefined") {
          window.localStorage.setItem("sfmd_access_token", accessToken);
          window.localStorage.setItem("sfmd_refresh_token", refreshToken);
          document.cookie = `sfmd_access_token=${accessToken}; path=/`;
        }
        set({ user, accessToken, refreshToken });
      },
      clearSession: () => {
        if (typeof window !== "undefined") {
          window.localStorage.removeItem("sfmd_access_token");
          window.localStorage.removeItem("sfmd_refresh_token");
          document.cookie = "sfmd_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        }
        set({ user: null, accessToken: null, refreshToken: null });
      },
    }),
    {
      name: "smartfmd-auth",
    },
  ),
);

