import { cn } from "@/lib/utils";

export function Table({ className, children }: { className?: string; children: React.ReactNode }) {
  return <table className={cn("w-full border-collapse text-left", className)}>{children}</table>;
}

export function TableHead({ children }: { children: React.ReactNode }) {
  return <thead className="text-xs uppercase tracking-[0.2em] text-foreground/45">{children}</thead>;
}

export function TableHeaderRow({ children }: { children: React.ReactNode }) {
  return <tr className="border-b border-border/70">{children}</tr>;
}

export function TableBody({ children }: { children: React.ReactNode }) {
  return <tbody>{children}</tbody>;
}

export function TableRow({ children }: { children: React.ReactNode }) {
  return <tr className="border-b border-border/40 text-sm text-foreground/80">{children}</tr>;
}

export function TableCell({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <td className={cn("px-3 py-3", className)}>{children}</td>;
}

export function TableHeader({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <th className={cn("px-3 py-3 font-medium", className)}>{children}</th>;
}

