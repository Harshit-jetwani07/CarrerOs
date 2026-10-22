import { ProgressBar } from "./ui/ProgressBar";

interface SkillBarProps {
  name: string;
  value: number;
  color?: "cobalt" | "gold" | "rust" | "ink";
}

export function SkillBar({ name, value, color = "cobalt" }: SkillBarProps) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-medium">{name}</span>
        <span className="text-slate">{Math.round(value)}%</span>
      </div>
      <ProgressBar value={value} color={color} />
    </div>
  );
}
