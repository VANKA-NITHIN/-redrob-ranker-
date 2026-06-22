import type { ReactNode } from "react"
import { motion } from "framer-motion"

interface PageHeaderProps {
  title: string
  description?: string
  actions?: ReactNode
  badge?: ReactNode
}

export function PageHeader({ title, description, actions, badge }: PageHeaderProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.4 }}
      className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border-light pb-5 mb-6"
    >
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-fluid-section font-semibold text-text-primary tracking-tight">
            {title}
          </h1>
          {badge}
        </div>
        {description && (
          <p className="text-fluid-small text-text-muted max-w-2xl">
            {description}
          </p>
        )}
      </div>
      
      {actions && (
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          {actions}
        </div>
      )}
    </motion.div>
  )
}
