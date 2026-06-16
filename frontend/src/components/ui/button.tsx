import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-[10px] text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        default: "bg-brand-600 text-white hover:bg-brand-700 shadow-sm hover:shadow-md",
        destructive: "bg-danger text-white hover:bg-red-600 shadow-sm",
        outline: "border border-border bg-surface hover:bg-surface-secondary text-text-secondary",
        secondary: "bg-surface-secondary text-text-secondary hover:bg-surface-tertiary",
        ghost: "text-text-muted hover:text-text-primary hover:bg-surface-secondary",
        link: "text-brand-600 underline-offset-4 hover:underline",
        gradient: "bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm hover:shadow-md hover:from-brand-700 hover:to-brand-600",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-[8px] px-3 text-xs",
        lg: "h-11 rounded-[12px] px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
