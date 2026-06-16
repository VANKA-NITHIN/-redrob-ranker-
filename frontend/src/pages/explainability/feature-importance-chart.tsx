import { motion } from "framer-motion"
import { Info } from "lucide-react"

export interface FeatureImportance {
  label: string
  contribution: number // can be positive or negative percentage
  description?: string
}

interface FeatureImportanceChartProps {
  features: FeatureImportance[]
}

function barColor(contribution: number): string {
  if (contribution >= 20) return "#10b981"
  if (contribution >= 10) return "#3b82f6"
  if (contribution >= 5) return "#8b5cf6"
  if (contribution > 0) return "#6366f1"
  return "#ef4444"
}

function barLabel(contribution: number): string {
  return contribution >= 0 ? `+${contribution}%` : `${contribution}%`
}

export function FeatureImportanceChart({ features }: FeatureImportanceChartProps) {
  const maxAbs = Math.max(...features.map((f) => Math.abs(f.contribution)), 1)

  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Feature Importance</h3>
        <Info className="w-3.5 h-3.5 text-text-dim" />
      </div>

      <div className="space-y-3">
        {features.map((feature, i) => {
          const color = barColor(feature.contribution)
          const widthPct = (Math.abs(feature.contribution) / maxAbs) * 100
          const isPositive = feature.contribution >= 0

          return (
            <motion.div
              key={feature.label}
              className="space-y-1"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.06 }}
            >
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-text-secondary font-medium">{feature.label}</span>
                  {feature.description && (
                    <span className="group relative">
                      <Info className="w-3 h-3 text-text-dim cursor-help" />
                      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 rounded-[6px] bg-surface border border-border/50 text-[10px] text-text-muted whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-sm">
                        {feature.description}
                      </span>
                    </span>
                  )}
                </div>
                <span
                  className="font-mono font-semibold text-xs"
                  style={{ color: isPositive ? "#10b981" : "#ef4444" }}
                >
                  {barLabel(feature.contribution)}
                </span>
              </div>

              <div className="relative h-2 rounded-full bg-surface-tertiary/50 overflow-hidden">
                <motion.div
                  className={`absolute top-0 h-full rounded-full ${isPositive ? "left-0" : "right-0"}`}
                  style={{ backgroundColor: color }}
                  initial={{ width: 0 }}
                  animate={{
                    width: `${widthPct}%`,
                    left: isPositive ? 0 : undefined,
                    right: isPositive ? undefined : 0,
                  }}
                  transition={{ duration: 0.8, ease: "easeOut", delay: i * 0.06 }}
                />
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
