import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-[8px] text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.97]",
  {
    variants: {
      variant: {
        default: "bg-surface-primary text-text-primary shadow-premium hover:shadow-premium-hover border border-border-light bg-gradient-to-b from-white/10 to-transparent",
        primary: "bg-brand-600 text-white hover:bg-brand-500 shadow-premium hover:shadow-premium-hover border border-brand-500/50 shadow-inner-button",
        destructive: "bg-danger text-white hover:bg-red-500 shadow-premium border border-red-500/50 shadow-inner-button",
        outline: "border border-border bg-transparent hover:bg-surface-secondary text-text-secondary hover:text-text-primary",
        secondary: "bg-surface-secondary text-text-primary hover:bg-surface-tertiary border border-transparent hover:border-border-light",
        ghost: "text-text-muted hover:text-text-primary hover:bg-surface-secondary",
        link: "text-brand-500 underline-offset-4 hover:underline",
        gradient: "bg-gradient-to-r from-brand-600 to-brand-400 text-white shadow-premium hover:shadow-premium-hover border border-brand-400/50 shadow-inner-button hover:from-brand-500 hover:to-brand-300",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-[6px] px-3 text-[13px]",
        lg: "h-10 rounded-[10px] px-8 text-sm",
        icon: "h-9 w-9",
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
