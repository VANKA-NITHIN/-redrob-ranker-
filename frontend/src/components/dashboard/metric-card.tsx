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
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      className="rounded-xl border border-border-light bg-surface/40 p-5 shadow-sm hover:shadow-premium transition-all duration-300 relative overflow-hidden group backdrop-blur-sm flex flex-col"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="flex items-center justify-between mb-4">
        <p className="text-[13px] font-medium text-text-muted flex items-center gap-2">
          {label}
        </p>
        <div
          className="w-8 h-8 rounded-[8px] flex items-center justify-center shrink-0 border border-border-light shadow-inner-button"
          style={{ background: `linear-gradient(135deg, ${color}22, transparent)` }}
        >
          <div style={{ color }}>{icon}</div>
        </div>
      </div>

      <div className="mt-auto">
        <p className="text-3xl font-semibold tracking-[-0.03em] text-text-primary mb-2">
          {value}
        </p>
        {trend !== undefined && (
          <div className="flex items-center gap-1.5">
            <span
              className={cn(
                "flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px]",
                trend >= 0 ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
              )}
            >
              {trend >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
              {Math.abs(trend)}%
            </span>
            <span className="text-[11px] text-text-dim">vs last month</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}
