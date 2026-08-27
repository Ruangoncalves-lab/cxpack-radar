import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

const Sheet = DialogPrimitive.Root
const SheetTrigger = DialogPrimitive.Trigger
const SheetClose = DialogPrimitive.Close

const SheetContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-ink/55 data-[state=open]:animate-in data-[state=closed]:animate-out" />
    <DialogPrimitive.Content
      ref={ref}
      className={cn("fixed inset-y-0 left-0 z-50 w-[min(88vw,360px)] border-r border-rule bg-paper p-5 shadow-[18px_0_50px_rgba(20,22,18,.2)]", className)}
      {...props}
    >
      <DialogPrimitive.Title className="sr-only">Menu principal</DialogPrimitive.Title>
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 grid size-10 place-items-center rounded-lg text-muted hover:bg-stock hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal">
        <X className="size-5" /><span className="sr-only">Fechar menu</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
))
SheetContent.displayName = DialogPrimitive.Content.displayName

export { Sheet, SheetClose, SheetContent, SheetTrigger }
