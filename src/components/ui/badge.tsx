import { cva, type VariantProps } from "class-variance-authority"
import type * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold leading-none",
  {
    variants: {
      variant: {
        default: "border-ink/15 bg-ink text-paper",
        outline: "border-rule bg-transparent text-ink",
        success: "border-success/25 bg-success/10 text-success",
        warning: "border-signal/25 bg-signal/10 text-[#9d2f1c]",
      },
    },
    defaultVariants: { variant: "default" },
  },
)

function Badge({ className, variant, ...props }: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
