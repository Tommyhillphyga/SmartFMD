"use client";

import { useMutation } from "@tanstack/react-query";
import { ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("Admin123!");

  const loginMutation = useMutation({
    mutationFn: api.login,
    onSuccess: (response) => {
      setSession({
        user: response.user,
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
      });
      router.push("/dashboard");
    },
  });

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.15fr_0.85fr]">
      <section className="grid-sheen hidden bg-card/30 p-12 lg:flex lg:flex-col lg:justify-between">
        <div className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.35em] text-primary">SmartFMD</p>
          <h1 className="mt-6 text-6xl leading-tight">
            Realtime fuel intelligence for Nigerian forecourts.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-foreground/70">
            Monitor active fueling, surface tamper conditions, rank station performance, and keep every
            attendant accountable from one command center.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {[
            "Live pump telemetry",
            "Fraud alerting engine",
            "Multi-station analytics",
          ].map((item) => (
            <div key={item} className="rounded-2xl border border-border/60 bg-background/45 p-5">
              <p className="text-sm text-foreground/55">{item}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="flex items-center justify-center p-6 lg:p-10">
        <Card className="w-full max-w-md bg-card/85 p-8 shadow-glow">
          <p className="text-xs uppercase tracking-[0.35em] text-primary">Operations Access</p>
          <h2 className="mt-4 text-4xl">Sign in</h2>
          <p className="mt-3 text-sm text-foreground/65">
            Demo credentials are prefilled so you can move straight into the MVP.
          </p>
          <form
            className="mt-8 space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              loginMutation.mutate({ email, password });
            }}
          >
            <Input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email address" />
            <Input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              type="password"
            />
            <Button className="w-full" type="submit" disabled={loginMutation.isPending}>
              {loginMutation.isPending ? "Signing in..." : "Access dashboard"}
              <ChevronRight className="h-4 w-4" />
            </Button>
          </form>
          {loginMutation.isError ? (
            <p className="mt-4 text-sm text-danger">
              {(loginMutation.error as Error).message || "Unable to sign in"}
            </p>
          ) : null}
        </Card>
      </section>
    </div>
  );
}
