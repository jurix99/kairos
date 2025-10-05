"use client"

import { useState, useEffect } from "react"
import { CalendarIcon, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { SiteHeader } from "@/components/site-header"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"
import type { Event, Category } from "@/lib/api"
import { MonthView } from "@/components/calendar/month-view"
import { WeekView } from "@/components/calendar/week-view"
import { DayView } from "@/components/calendar/day-view"
import { Card } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { EventDialog } from "@/components/event-dialog"

type ViewMode = "month" | "week" | "day"

export default function CalendarPage() {
  const { user } = useAuth()
  const [viewMode, setViewMode] = useState<ViewMode>("month")
  const [currentDate, setCurrentDate] = useState(new Date())
  const [events, setEvents] = useState<Event[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [eventsData, categoriesData] = await Promise.all([
        apiClient.getEvents(),
        apiClient.getCategories()
      ])
      setEvents(eventsData)
      setCategories(categoriesData)
    } catch (error) {
      console.error("Failed to load calendar data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const navigateDate = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate)
    
    if (viewMode === "month") {
      newDate.setMonth(newDate.getMonth() + (direction === "next" ? 1 : -1))
    } else if (viewMode === "week") {
      newDate.setDate(newDate.getDate() + (direction === "next" ? 7 : -7))
    } else {
      newDate.setDate(newDate.getDate() + (direction === "next" ? 1 : -1))
    }
    
    setCurrentDate(newDate)
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const formatDateHeader = () => {
    if (viewMode === "month") {
      return currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })
    } else if (viewMode === "week") {
      const weekStart = new Date(currentDate)
      weekStart.setDate(currentDate.getDate() - currentDate.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      
      return `${weekStart.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${weekEnd.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`
    } else {
      return currentDate.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })
    }
  }

  const handleEventClick = (event: Event) => {
    // TODO: Open event details dialog
    console.log("Event clicked:", event)
  }

  const handleDateClick = (date: Date) => {
    setCurrentDate(date)
    if (viewMode === "month") {
      setViewMode("day")
    }
  }

  if (isLoading) {
    return (
      <>
        <SiteHeader user={user} title="Calendar" icon={CalendarIcon} />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <div>Loading calendar...</div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <SiteHeader user={user} title="Calendar" icon={CalendarIcon} />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
        {/* Calendar Controls */}
        <Card className="p-4">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            {/* Date Navigation */}
            <div className="flex items-center gap-2 flex-wrap">
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateDate("prev")}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="min-w-[200px] text-center font-semibold">
                {formatDateHeader()}
              </div>
              
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateDate("next")}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              
              <Button variant="outline" onClick={goToToday}>
                Today
              </Button>
            </div>

            {/* Add Event Button & View Mode Selector */}
            <div className="flex items-center gap-4 flex-wrap">
              <EventDialog
                categories={categories}
                onEventCreated={loadData}
                defaultDate={currentDate}
              />
              {/* Category Filter */}
              <Select
                value={selectedCategoryId || "all"}
                onValueChange={(value) => setSelectedCategoryId(value === "all" ? null : value)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: category.color }}
                        />
                        {category.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <ToggleGroup type="single" value={viewMode} onValueChange={(value) => value && setViewMode(value as ViewMode)}>
                <ToggleGroupItem value="month" aria-label="Month view">
                  Month
                </ToggleGroupItem>
                <ToggleGroupItem value="week" aria-label="Week view">
                  Week
                </ToggleGroupItem>
                <ToggleGroupItem value="day" aria-label="Day view">
                  Day
                </ToggleGroupItem>
              </ToggleGroup>
            </div>
          </div>
        </Card>

        {/* Calendar Views */}
        <Card className="flex-1 overflow-hidden">
          {viewMode === "month" && (
            <MonthView
              currentDate={currentDate}
              events={events}
              categories={categories}
              selectedCategoryId={selectedCategoryId}
              onDateClick={handleDateClick}
              onEventClick={handleEventClick}
            />
          )}
          {viewMode === "week" && (
            <WeekView
              currentDate={currentDate}
              events={events}
              categories={categories}
              selectedCategoryId={selectedCategoryId}
              onDateClick={handleDateClick}
              onEventClick={handleEventClick}
            />
          )}
          {viewMode === "day" && (
            <DayView
              currentDate={currentDate}
              events={events}
              categories={categories}
              selectedCategoryId={selectedCategoryId}
              onEventClick={handleEventClick}
            />
          )}
        </Card>
      </div>

      {/* Floating Action Button for mobile */}
      <div className="fixed bottom-6 right-6 lg:hidden">
        <EventDialog
          categories={categories}
          onEventCreated={loadData}
          defaultDate={currentDate}
          trigger={
            <Button size="lg" className="h-14 w-14 rounded-full shadow-lg">
              <CalendarIcon className="h-6 w-6" />
            </Button>
          }
        />
      </div>
    </>
  )
}
