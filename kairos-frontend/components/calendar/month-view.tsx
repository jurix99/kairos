"use client"

import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Event, Category } from "@/lib/api"

interface MonthViewProps {
  currentDate: Date
  events: Event[]
  categories: Category[]
  selectedCategoryId: string | null
  onDateClick: (date: Date) => void
  onEventClick: (event: Event) => void
}

export function MonthView({
  currentDate,
  events,
  categories,
  selectedCategoryId,
  onDateClick,
  onEventClick,
}: MonthViewProps) {
  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay()
  }

  const getEventsForDate = (date: Date) => {
    return events.filter((event) => {
      const eventDate = new Date(event.start_time)
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear()
      )
    })
  }

  const isEventVisible = (event: Event) => {
    return selectedCategoryId === null || event.category_id === selectedCategoryId
  }

  const getEventOpacity = (event: Event) => {
    return isEventVisible(event) ? 1 : 0.3
  }

  const getCategoryColor = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.color || "#6366f1"
  }

  const daysInMonth = getDaysInMonth(currentDate)
  const firstDay = getFirstDayOfMonth(currentDate)
  const today = new Date()

  const days = []
  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  // Empty cells for days before the first day of the month
  for (let i = 0; i < firstDay; i++) {
    days.push(null)
  }

  // Days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day)
  }

  const isToday = (day: number) => {
    return (
      day === today.getDate() &&
      currentDate.getMonth() === today.getMonth() &&
      currentDate.getFullYear() === today.getFullYear()
    )
  }

  const handleDayClick = (day: number) => {
    const clickedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day)
    onDateClick(clickedDate)
  }

  return (
    <div className="p-4 h-full overflow-auto">
      {/* Days of week header */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {daysOfWeek.map((day) => (
          <div
            key={day}
            className="text-center text-sm font-semibold text-muted-foreground py-2"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {days.map((day, index) => {
          if (!day) {
            return <div key={`empty-${index}`} className="min-h-[100px]" />
          }

          const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day)
          const dayEvents = getEventsForDate(date)

          return (
            <div
              key={day}
              onClick={() => handleDayClick(day)}
              className={cn(
                "min-h-[100px] p-2 rounded-lg border cursor-pointer transition-all duration-200 hover:border-purple-500/50 hover:bg-accent/50",
                isToday(day)
                  ? "bg-purple-600/10 border-purple-500/50"
                  : "bg-card border-border"
              )}
            >
              <div
                className={cn(
                  "text-sm font-medium mb-1",
                  isToday(day) ? "text-purple-400" : "text-foreground"
                )}
              >
                {day}
              </div>

              {/* Events */}
              <div className="space-y-1">
                {dayEvents.slice(0, 3).map((event) => (
                  <div
                    key={event.id}
                    onClick={(e) => {
                      e.stopPropagation()
                      onEventClick(event)
                    }}
                    className={cn(
                      "text-xs p-1 rounded truncate cursor-pointer transition-all duration-200",
                      isEventVisible(event)
                        ? "hover:opacity-80"
                        : "hover:opacity-50 grayscale"
                    )}
                    style={{
                      backgroundColor: getCategoryColor(event.category_id),
                      opacity: getEventOpacity(event),
                    }}
                    title={event.title}
                  >
                    {event.title}
                  </div>
                ))}
                {dayEvents.length > 3 && (
                  <div className="text-xs text-muted-foreground font-medium text-center">
                    +{dayEvents.length - 3} more
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
