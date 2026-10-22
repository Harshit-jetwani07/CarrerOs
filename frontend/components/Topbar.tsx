import { AIEngineBadge } from "@/components/AIEngineBadge";
import { ThemeToggle } from "@/components/ThemeToggle";

interface TopbarProps {
  title: string;
  subtitle?: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  return (
    <div className="mb-8 flex items-start justify-between gap-4">
      <div><h1 className="text-2xl font-semibold tracking-tight">{title}</h1>{subtitle && <p className="text-slate mt-1">{subtitle}</p>}</div>
      <div className="flex items-center gap-3"><AIEngineBadge /><ThemeToggle /></div>
    </div>
  );
}
