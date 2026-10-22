interface ReadinessGaugeProps {
  value: number; // 0-100
  size?: number;
}

/**
 * The hero visual of the product: a single arc gauge showing overall
 * career readiness. This is the most characteristic artifact in
 * CareerOS's world, so it earns the "big visual" hero treatment
 * rather than a generic stat block.
 */
export function ReadinessGauge({ value, size = 220 }: ReadinessGaugeProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const radius = size / 2 - 14;
  const circumference = Math.PI * radius; // half circle
  const offset = circumference * (1 - clamped / 100);
  const center = size / 2;

  return (
    <div className="relative" style={{ width: size, height: size / 2 + 24 }}>
      <svg width={size} height={size / 2 + 24} viewBox={`0 0 ${size} ${size / 2 + 24}`}>
        <path
          d={`M 14 ${center} A ${radius} ${radius} 0 0 1 ${size - 14} ${center}`}
          fill="none"
          stroke="currentColor"
          className="text-black/[0.07]"
          strokeWidth={14}
          strokeLinecap="round"
        />
        <path
          d={`M 14 ${center} A ${radius} ${radius} 0 0 1 ${size - 14} ${center}`}
          fill="none"
          stroke="currentColor"
          className="text-gold"
          strokeWidth={14}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute inset-x-0 bottom-0 text-center">
        <div className="text-4xl font-display font-semibold">{clamped}%</div>
        <div className="text-sm text-slate">career readiness</div>
      </div>
    </div>
  );
}
