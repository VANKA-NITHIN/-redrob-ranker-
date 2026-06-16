import { motion } from "framer-motion"

interface RingGaugeProps {
  value: number
  size?: number
  strokeWidth?: number
  color?: string
  delay?: number
  className?: string
}

export function RingGauge({
  value,
  size = 72,
  strokeWidth = 5,
  color = "#6366f1",
  delay = 0,
  className = "",
}: RingGaugeProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const clampedValue = Math.min(Math.max(value, 0), 100)

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{
            strokeDashoffset: circumference - (clampedValue / 100) * circumference,
          }}
          transition={{ duration: 1.2, ease: "easeOut", delay }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-lg font-bold font-mono"
          style={{ color }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 + delay }}
        >
          {clampedValue}%
        </motion.span>
      </div>
    </div>
  )
}
