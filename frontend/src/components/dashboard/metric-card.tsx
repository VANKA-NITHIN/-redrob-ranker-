import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown } from "lucide-react"

interface MetricCardProps {
  label: string
  value: string
  icon: React.ReactNode
  trend?: number
  color?: string
  delay?: number
}

export function MetricCard({
  label,
  value,
  icon,
  trend,
  color = "#6366f1",
  delay = 0,
}: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className="rounded-[14px] border border-border/50 bg-surface p-4 hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 relative overflow-hidden group"
    >
      {/* Top accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-[3px] opacity-80"
        style={{ background: `linear-gradient(90deg, ${color}, ${color}88)` }}
      />

      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-text-muted">
            {label}
          </p>
          <p
            className="text-2xl font-bold tracking-tight"
            style={{ color }}
          >
            {value}
          </p>
        </div>
        <div
          className="w-9 h-9 rounded-[10px] flex items-center justify-center shrink-0"
          style={{ background: `${color}15` }}
        >
          {icon}
        </div>
      </div>

      {trend !== undefined && (
        <div className="flex items-center gap-1 mt-2">
          {trend >= 0 ? (
            <TrendingUp className="w-3 h-3 text-success" />
          ) : (
            <TrendingDown className="w-3 h-3 text-danger" />
          )}
          <span
            className={cn(
              "text-xs font-medium",
              trend >= 0 ? "text-success" : "text-danger"
            )}
          >
            {Math.abs(trend)}%
          </span>
          <span className="text-[10px] text-text-dim">vs last run</span>
        </div>
      )}
    </motion.div>
  )
}
