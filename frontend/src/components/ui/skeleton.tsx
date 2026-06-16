import { cn } from "@/lib/utils"

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-[8px] bg-surface-tertiary/50",
        className
      )}
      {...props}
    />
  )
}

export function MetricCardSkeleton() {
  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-4 space-y-3">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-16" />
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      <Skeleton className="h-10 w-full" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  )
}
