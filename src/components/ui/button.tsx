import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex min-h-11 items-center justify-center gap-2 whitespace-nowrap rounded-[10px] px-4 text-sm font-semibold transition-[background,color,border-color,transform] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal focus-visible:ring-offset-2 focus-visible:ring-offset-paper disabled:pointer-events-none disabled:opacity-45 active:translate-y-px",
  {
    variants: {
      variant: {
        default: "bg-ink text-paper hover:bg-ink/88",
        signal: "bg-signal text-ink hover:bg-[#cf4328]",
        outline: "border border-rule bg-paper text-ink hover:border-ink/45 hover:bg-stock",
        ghost: "text-ink hover:bg-stock",
        destructive: "border border-danger/35 text-danger hover:bg-danger hover:text-white",
      },
      size: {
        default: "h-11",
        sm: "h-9 min-h-9 px-3 text-xs",
        lg: "h-12 px-6",
        icon: "size-11 p-0",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  },
)
Button.displayName = "Button"

export { Button, buttonVariants }
