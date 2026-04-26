"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { useAuthStore } from "@/store/auth-store";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const accessToken = useAuthStore((state) => state.accessToken);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && !accessToken && typeof window !== "undefined") {
      router.replace("/login");
    }
  }, [accessToken, hydrated, router]);

  if (!hydrated) {
    return <div className="min-h-screen animate-pulse bg-background" />;
  }

  return <>{children}</>;
}

