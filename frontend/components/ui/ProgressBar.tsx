import clsx from "clsx";

interface ProgressBarProps {
  value: number; // 0-100
  color?: "cobalt" | "gold" | "rust" | "ink";
  className?: string;
}

const colorMap = {
  cobalt: "bg-cobalt",
  gold: "bg-gold",
  rust: "bg-rust",
  ink: "bg-ink",
};

export function ProgressBar({ value, color = "cobalt", className }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={clsx("h-2 w-full rounded-full bg-black/[0.06] overflow-hidden", className)}>
      <div
        className={clsx("h-full rounded-full transition-all duration-500", colorMap[color])}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
