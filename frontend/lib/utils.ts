import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: "NGN",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat("en-NG", {
    maximumFractionDigits: 2,
  }).format(value);
}

export function severityTone(severity: string) {
  switch (severity) {
    case "critical":
      return "bg-danger/15 text-danger";
    case "medium":
      return "bg-warning/15 text-warning";
    default:
      return "bg-primary/10 text-primary";
  }
}

