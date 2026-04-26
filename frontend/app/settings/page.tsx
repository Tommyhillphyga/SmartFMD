"use client";

import { AppShell } from "@/components/dashboard/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/auth-store";
import { useUiStore } from "@/store/ui-store";

export default function SettingsPage() {
  const theme = useUiStore((state) => state.theme);
  const toggleTheme = useUiStore((state) => state.toggleTheme);
  const user = useAuthStore((state) => state.user);

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Settings</p>
          <h1 className="mt-3 text-5xl">Operational preferences</h1>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardTitle>Appearance</CardTitle>
            <CardDescription className="mt-2">Switch between light and dark views without interrupting live monitoring.</CardDescription>
            <div className="mt-6 flex items-center justify-between">
              <span className="text-sm text-foreground/70">Dark mode</span>
              <Switch checked={theme === "dark"} onCheckedChange={toggleTheme} />
            </div>
          </Card>

          <Card>
            <CardTitle>Current session</CardTitle>
            <CardDescription className="mt-2">Identity, role, and environment metadata for the signed-in operator.</CardDescription>
            <div className="mt-6 space-y-3 text-sm">
              <p>Name: {user?.full_name ?? "Unknown"}</p>
              <p>Email: {user?.email ?? "Unknown"}</p>
              <div>
                <Badge variant="info">{user?.role?.replaceAll("_", " ") ?? "guest"}</Badge>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
