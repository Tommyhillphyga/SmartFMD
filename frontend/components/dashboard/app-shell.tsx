"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Gauge, LayoutDashboard, LogOut, MapPinned, OctagonAlert, Settings, Wrench } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useUiStore } from "@/store/ui-store";

import { AuthGate } from "../auth-gate";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/stations", label: "Stations", icon: MapPinned },
  { href: "/alerts", label: "Alerts", icon: OctagonAlert },
  { href: "/transactions", label: "Transactions", icon: Gauge },
  { href: "/analytics", label: "Analytics", icon: Gauge },
  { href: "/devices", label: "Devices", icon: Wrench },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, clearSession } = useAuthStore();
  const { theme, toggleTheme } = useUiStore();

  return (
    <AuthGate>
      <div className="grid min-h-screen lg:grid-cols-[280px_1fr]">
        <aside className="grid-sheen border-r border-border/70 bg-card/55 p-6 backdrop-blur-xl">
          <div className="rounded-2xl bg-gradient-to-br from-primary/80 via-primary/60 to-accent/70 p-5 text-white shadow-glow">
            <p className="text-xs uppercase tracking-[0.35em] text-white/70">SmartFMD</p>
            <h1 className="mt-3 text-2xl">Fuel Integrity Command Center</h1>
            <p className="mt-3 text-sm text-white/80">
              Multi-station visibility for live fueling, tamper alerts, and operator accountability.
            </p>
          </div>

          <nav className="mt-8 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-4 py-3 text-sm transition",
                    active
                      ? "bg-primary/12 text-primary"
                      : "text-foreground/70 hover:bg-muted/50 hover:text-foreground",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto rounded-2xl border border-border/60 bg-background/50 p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-foreground/70">Theme</span>
              <Switch checked={theme === "dark"} onCheckedChange={toggleTheme} />
            </div>
            <div className="mt-4 text-sm text-foreground/75">
              <p className="font-semibold">{user?.full_name}</p>
              <p className="capitalize text-foreground/55">{user?.role?.replaceAll("_", " ")}</p>
            </div>
            <Button
              variant="secondary"
              className="mt-4 w-full"
              onClick={() => {
                clearSession();
                router.push("/login");
              }}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </aside>

        <main className="min-h-screen bg-background/70">
          <div className="mx-auto max-w-7xl p-6 lg:p-8">{children}</div>
        </main>
      </div>
    </AuthGate>
  );
}

