import clsx from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  tone?: "high" | "medium" | "low" | "neutral";
}

const toneMap = {
  high: "bg-rust-light text-rust",
  medium: "bg-gold-light text-gold",
  low: "bg-cobalt-light text-cobalt-dark",
  neutral: "bg-black/5 text-slate",
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span className={clsx("inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium", toneMap[tone])}>
      {children}
    </span>
  );
}
