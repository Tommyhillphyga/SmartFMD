import type { Metadata } from "next";

import { Providers } from "@/components/providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "SMART FUEL DISPENSER MONITORING DASHBOARD",
  description: "Realtime monitoring, fraud detection, and analytics for retrofitted fuel dispensers.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

