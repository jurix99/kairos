"use client"

import { AppSidebar } from "@/components/app-sidebar"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { useAuth } from "@/contexts/auth-context"

interface GoalsLayoutProps {
  children: React.ReactNode
}

export default function GoalsLayout({
  children,
}: GoalsLayoutProps) {
  const { user } = useAuth()

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} />
      <SidebarInset>
        <div className="flex flex-1 flex-col gap-4 min-h-screen">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
