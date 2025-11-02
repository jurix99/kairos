"use client"

import * as React from "react"
import {
  IconCalendar,
  IconChartBar,
  IconDashboard,
  IconHelp,
  IconRobot,
  IconSettings,
  IconTarget
} from "@tabler/icons-react"
import { Calendar } from "lucide-react"
import { useRouter } from "next/navigation"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import type { User } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  user: User
}

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const router = useRouter()
  const { signOut } = useAuth()

  const handleSignOut = () => {
    signOut()
    router.push('/login')
  }

  const data = {
    user: {
      name: user.name,
      email: user.email,
      avatar: user.picture || "/avatars/default.jpg",
    },
    navMain: [
      {
        title: "Dashboard",
        url: "/dashboard",
        icon: IconDashboard,
      },
      {
        title: "Calendar",
        url: "/calendar",
        icon: IconCalendar,
      },
      {
        title: "Assistant",
        url: "/assistant",
        icon: IconRobot,
      },
      {
        title: "Objectifs",
        url: "/goals",
        icon: IconTarget,
      }
    ],
    navSecondary: [
      {
        title: "Settings",
        url: "/settings",
        icon: IconSettings,
      },
      {
        title: "Help",
        url: "/help",
        icon: IconHelp,
      },
    ],
  }

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/dashboard">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                  <Calendar className="size-4" />
                </div>
                <span className="text-base font-semibold">KAIROS</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} onSignOut={handleSignOut} />
      </SidebarFooter>
    </Sidebar>
  )
}
