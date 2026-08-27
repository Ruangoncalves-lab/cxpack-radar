import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { Check, ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

const Select = SelectPrimitive.Root
const SelectValue = SelectPrimitive.Value

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-12 w-full items-center justify-between rounded-[10px] border border-rule bg-white px-3.5 text-[15px] text-ink outline-none focus:border-ink focus:ring-2 focus:ring-signal/20 data-[placeholder]:text-muted/85",
      className,
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild><ChevronDown className="size-4 text-muted" /></SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
))
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      position={position}
      className={cn("z-50 min-w-[8rem] overflow-hidden rounded-xl border border-rule bg-white p-1.5 text-ink shadow-[0_18px_50px_rgba(20,22,18,.16)]", className)}
      {...props}
    >
      <SelectPrimitive.Viewport>{children}</SelectPrimitive.Viewport>
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
))
SelectContent.displayName = SelectPrimitive.Content.displayName

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn("relative flex min-h-10 cursor-default select-none items-center rounded-lg py-2 pl-8 pr-3 text-sm outline-none focus:bg-stock data-[disabled]:opacity-50", className)}
    {...props}
  >
    <span className="absolute left-2.5 flex size-4 items-center justify-center">
      <SelectPrimitive.ItemIndicator><Check className="size-4" /></SelectPrimitive.ItemIndicator>
    </span>
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
))
SelectItem.displayName = SelectPrimitive.Item.displayName

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue }
