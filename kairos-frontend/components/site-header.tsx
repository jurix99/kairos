import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Calendar } from "lucide-react"
import type { User } from "@/lib/api"
import type { LucideIcon } from "lucide-react"

interface SiteHeaderProps {
  user?: User
  title?: string
  icon?: LucideIcon | React.ComponentType<{ className?: string }>
}

export function SiteHeader({ user, title = "Dashboard", icon: Icon = Calendar }: SiteHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-2 data-[orientation=vertical]:h-4"
        />
        <div className="flex items-center gap-2">
          <Icon className="size-5 text-purple-500" />
          <h1 className="text-base font-medium">{title}</h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {user && (
            <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
              <span>Welcome, {user.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
