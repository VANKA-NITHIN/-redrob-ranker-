import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider border transition-all duration-200",
  {
    variants: {
      variant: {
        verified:
          "bg-success/8 text-success border-success/15",
        suspicious:
          "bg-warning/8 text-warning border-warning/15",
        honeypot:
          "bg-danger/8 text-danger border-danger/15 animate-pulse",
        default:
          "bg-surface-secondary text-text-muted border-border/50",
        brand:
          "bg-brand-100 text-brand-700 border-brand-200",
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
