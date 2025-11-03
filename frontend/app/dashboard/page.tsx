"use client"

import { useEffect, useState } from "react"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { ChartStatusDistribution } from "@/components/chart-status-distribution"
import { ChartCategoryPerformance } from "@/components/chart-category-performance"
import { ChartPriorityDistribution } from "@/components/chart-priority-distribution"
import { CategoryStatsTable } from "@/components/category-stats-table"
import { SectionCards } from "@/components/section-cards"
import { SiteHeader } from "@/components/site-header"
import { NotificationsBell } from "@/components/notifications-bell"
import { SuggestionsPanel } from "@/components/suggestions-panel"
import { useAuth } from "@/contexts/auth-context"
import { apiClient, type Event, type Category } from "@/lib/api"

export default function Page() {
  const { user } = useAuth()
  const [events, setEvents] = useState<Event[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load data from API
  useEffect(() => {
    const loadData = async () => {
      if (!user) return

      try {
        setDataLoading(true)
        setError(null)

        // Load events from 30 days ago to 30 days ahead for dashboard analytics
        const now = new Date()
        const startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) // 30 days ago
        const endDate = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000) // 30 days ahead

        const [eventsData, categoriesData] = await Promise.all([
          apiClient.getEvents(startDate, endDate),
          apiClient.getCategories()
        ])

        setEvents(eventsData)
        setCategories(categoriesData)
      } catch (err) {
        console.error('Error loading data:', err)
        setError('Failed to load data. Please check your backend connection.')
      } finally {
        setDataLoading(false)
      }
    }

    loadData()
  }, [user])

  return (
    <>
      <SiteHeader user={user} />
      <div className="flex flex-1 flex-col">
        <div className="flex flex-1 flex-col gap-2">
          {error && (
            <div className="mx-4 mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
              {error}
            </div>
          )}
          {dataLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
          ) : (
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              {/* KPI Cards */}
              <SectionCards events={events} categories={categories} />
              
              {/* Suggestions Panel */}
              <div className="px-4 lg:px-6">
                <SuggestionsPanel />
              </div>
              
              {/* Main Chart - Event Progress Over Time */}
              <div className="px-4 lg:px-6">
                <ChartAreaInteractive events={events} />
              </div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 px-4 lg:px-6 md:gap-6">
                <ChartStatusDistribution events={events} />
                <ChartCategoryPerformance events={events} categories={categories} />
                <ChartPriorityDistribution events={events} />
              </div>

              {/* Category Statistics Table */}
              <div className="px-4 lg:px-6">
                <CategoryStatsTable events={events} categories={categories} />
              </div>
            </div>
          )}
        </div>
      </div>
      <NotificationsBell categories={categories} />
    </>
  )
}
