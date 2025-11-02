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
import { EditEventDialog } from "@/components/edit-event-dialog"
import { NotificationsBell } from "@/components/notifications-bell"

type ViewMode = "month" | "week" | "day"

export default function CalendarPage() {
  const { user } = useAuth()
  const [viewMode, setViewMode] = useState<ViewMode>("month")
  const [currentDate, setCurrentDate] = useState(new Date())
  const [events, setEvents] = useState<Event[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogStartTime, setDialogStartTime] = useState<Date | undefined>()
  const [dialogEndTime, setDialogEndTime] = useState<Date | undefined>()
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)

  useEffect(() => {
    loadData()
  }, [currentDate, viewMode, selectedCategoryId])

  // Helper functions to calculate date ranges for each view
  const getDateRange = () => {
    const start = new Date(currentDate)
    const end = new Date(currentDate)

    if (viewMode === "month") {
      // Get first day of month
      start.setDate(1)
      start.setHours(0, 0, 0, 0)
      
      // Get last day of month
      end.setMonth(end.getMonth() + 1)
      end.setDate(0)
      end.setHours(23, 59, 59, 999)
    } else if (viewMode === "week") {
      // Get start of week (Sunday)
      const dayOfWeek = start.getDay()
      start.setDate(start.getDate() - dayOfWeek)
      start.setHours(0, 0, 0, 0)
      
      // Get end of week (Saturday)
      end.setDate(start.getDate() + 6)
      end.setHours(23, 59, 59, 999)
    } else { // day view
      start.setHours(0, 0, 0, 0)
      end.setHours(23, 59, 59, 999)
    }

    return { start, end }
  }

  const loadData = async () => {
    try {
      setIsLoading(true)
      const { start, end } = getDateRange()
      
      const [eventsData, categoriesData] = await Promise.all([
        apiClient.getEvents(start, end, selectedCategoryId || undefined),
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

  // Format date to ISO string in local timezone (not UTC)
  const formatDateTimeForAPI = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, "0")
    const day = String(date.getDate()).padStart(2, "0")
    const hours = String(date.getHours()).padStart(2, "0")
    const minutes = String(date.getMinutes()).padStart(2, "0")
    const seconds = String(date.getSeconds()).padStart(2, "0")
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
  }

  const handleEventClick = (event: Event) => {
    setSelectedEvent(event)
    setEditDialogOpen(true)
  }

  const handleDateClick = (date: Date) => {
    setCurrentDate(date)
    if (viewMode === "month") {
      setViewMode("day")
    }
  }

  const handleEventDrop = async (event: Event, newStartTime: Date) => {
    try {
      // Calculate duration
      const oldStart = new Date(event.start_time)
      const oldEnd = new Date(event.end_time)
      const duration = oldEnd.getTime() - oldStart.getTime()

      // Calculate new end time
      const newEndTime = new Date(newStartTime.getTime() + duration)

      // Update event (use local timezone, not UTC)
      await apiClient.updateEvent(event.id, {
        start_time: formatDateTimeForAPI(newStartTime),
        end_time: formatDateTimeForAPI(newEndTime),
      })

      // Reload events
      await loadData()
    } catch (error) {
      console.error("Failed to update event:", error)
      alert("Failed to move event. Please try again.")
    }
  }

  const handleTimeSlotClick = (date: Date, hour: number) => {
    const startTime = new Date(date)
    startTime.setHours(hour, 0, 0, 0)
    
    const endTime = new Date(startTime)
    endTime.setHours(hour + 1, 0, 0, 0)

    setDialogStartTime(startTime)
    setDialogEndTime(endTime)
    setDialogOpen(true)
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
      <SiteHeader 
        user={user} 
        title="Calendar" 
        icon={CalendarIcon}
        controls={
          <div className="flex items-center gap-1 lg:gap-2 w-full min-w-0">
            {/* Date Navigation */}
            <div className="flex items-center gap-1 flex-shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateDate("prev")}
                className="h-7 w-7 lg:h-9 lg:w-9 p-0"
              >
                <ChevronLeft className="h-3 w-3 lg:h-4 lg:w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateDate("next")}
                className="h-7 w-7 lg:h-9 lg:w-9 p-0"
              >
                <ChevronRight className="h-3 w-3 lg:h-4 lg:w-4" />
              </Button>
            </div>

            {/* Date display - center */}
            <div className="flex-1 text-center font-semibold text-xs sm:text-sm lg:text-base px-1 lg:px-4 min-w-0">
              <span className="truncate block">
                {formatDateHeader()}
              </span>
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-1 lg:gap-3 flex-shrink-0">
              {/* Today button */}
              <Button variant="outline" size="sm" onClick={goToToday} className="hidden sm:inline-flex h-7 lg:h-9 text-xs lg:text-sm px-2 lg:px-4">
                Today
              </Button>
              
              {/* Desktop controls */}
              <div className="hidden md:flex items-center gap-1 lg:gap-3">
                <EventDialog
                  categories={categories}
                  onEventCreated={() => {
                    loadData()
                    setDialogOpen(false)
                  }}
                  defaultDate={currentDate}
                  defaultStartTime={dialogStartTime}
                  defaultEndTime={dialogEndTime}
                  open={dialogOpen}
                  onOpenChange={setDialogOpen}
                  trigger={
                    <Button size="sm" className="h-7 lg:h-9 text-xs lg:text-sm px-2 lg:px-4">
                      <span className="lg:hidden">Add</span>
                      <span className="hidden lg:inline">Add Event</span>
                    </Button>
                  }
                />
                
                <Select
                  value={selectedCategoryId || "all"}
                  onValueChange={(value) => setSelectedCategoryId(value === "all" ? null : value)}
                >
                  <SelectTrigger className="w-[100px] lg:w-[160px] h-7 lg:h-9 text-xs lg:text-sm">
                    <SelectValue placeholder="All" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2 h-2 lg:w-3 lg:h-3 rounded-full"
                            style={{ backgroundColor: category.color }}
                          />
                          {category.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* View selector - responsive */}
              <ToggleGroup type="single" value={viewMode} onValueChange={(value) => value && setViewMode(value as ViewMode)} size="sm">
                <ToggleGroupItem value="month" aria-label="Month view" className="text-xs lg:text-sm px-1 lg:px-3 h-7 lg:h-9 w-7 lg:w-auto">
                  <span className="lg:hidden">M</span>
                  <span className="hidden lg:inline">Month</span>
                </ToggleGroupItem>
                <ToggleGroupItem value="week" aria-label="Week view" className="text-xs lg:text-sm px-1 lg:px-3 h-7 lg:h-9 w-7 lg:w-auto">
                  <span className="lg:hidden">W</span>
                  <span className="hidden lg:inline">Week</span>
                </ToggleGroupItem>
                <ToggleGroupItem value="day" aria-label="Day view" className="text-xs lg:text-sm px-1 lg:px-3 h-7 lg:h-9 w-7 lg:w-auto">
                  <span className="lg:hidden">D</span>
                  <span className="hidden lg:inline">Day</span>
                </ToggleGroupItem>
              </ToggleGroup>
            </div>
          </div>
        }
      />
      <div className="flex flex-1 flex-col h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)]">
        {/* Calendar Views */}
        <div className="flex-1 overflow-hidden min-h-0 p-4 lg:p-6">
          <Card className="h-full overflow-hidden">
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
                onEventDrop={handleEventDrop}
                onTimeSlotClick={handleTimeSlotClick}
              />
            )}
            {viewMode === "day" && (
              <DayView
                currentDate={currentDate}
                events={events}
                categories={categories}
                selectedCategoryId={selectedCategoryId}
                onEventClick={handleEventClick}
                onEventDrop={handleEventDrop}
                onTimeSlotClick={handleTimeSlotClick}
              />
            )}
          </Card>
        </div>
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

      {/* Edit Event Dialog */}
      <EditEventDialog
        event={selectedEvent}
        categories={categories}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onEventUpdated={loadData}
        onEventDeleted={loadData}
      />
      
      <NotificationsBell categories={categories} />
    </>
  )
}
