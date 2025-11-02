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
  controls?: React.ReactNode
}

export function SiteHeader({ user, title = "Dashboard", icon: Icon = Calendar, controls }: SiteHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex w-full items-center gap-1 px-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-1 data-[orientation=vertical]:h-4"
        />
        <div className="flex items-center gap-2 flex-shrink-0 min-w-0">
          <Icon className="size-4 lg:size-5 text-purple-500 flex-shrink-0" />
          <h1 className="text-sm lg:text-base font-medium truncate">{title}</h1>
        </div>
        
        {/* Custom controls */}
        {controls && (
          <div className="flex-1 flex items-center justify-center min-w-0 mx-2">
            {controls}
          </div>
        )}
        
        <div className="flex items-center gap-2 flex-shrink-0">
          {user && (
            <div className="hidden lg:flex items-center gap-2 text-sm text-muted-foreground">
              <span>Welcome, {user.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
