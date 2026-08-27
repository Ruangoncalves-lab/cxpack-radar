import * as React from "react"
import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "flex h-12 w-full rounded-[10px] border border-rule bg-white px-3.5 text-[15px] text-ink shadow-[0_1px_0_rgba(20,22,18,.04)] outline-none placeholder:text-muted/85 focus:border-ink focus:ring-2 focus:ring-signal/20 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  ),
)
Input.displayName = "Input"

export { Input }
