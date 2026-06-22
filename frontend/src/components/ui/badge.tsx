import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-[0.03em] border transition-all duration-300 backdrop-blur-md",
  {
    variants: {
      variant: {
        verified:
          "bg-success/10 text-success border-success/20 shadow-[0_0_8px_rgba(16,185,129,0.15)]",
        suspicious:
          "bg-warning/10 text-warning border-warning/20 shadow-[0_0_8px_rgba(245,158,11,0.15)]",
        honeypot:
          "bg-danger/10 text-danger border-danger/20 shadow-[0_0_8px_rgba(239,68,68,0.15)] animate-pulse-slow",
        default:
          "bg-surface-secondary/50 text-text-muted border-border-light shadow-sm",
        brand:
          "bg-brand-500/10 text-brand-400 border-brand-500/20 shadow-[0_0_8px_rgba(139,92,246,0.15)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
