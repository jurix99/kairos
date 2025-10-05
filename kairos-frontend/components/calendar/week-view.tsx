"use client"

import { useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import type { Event, Category } from "@/lib/api"
import { ScrollArea } from "@/components/ui/scroll-area"

interface WeekViewProps {
  currentDate: Date
  events: Event[]
  categories: Category[]
  selectedCategoryId: string | null
  onDateClick: (date: Date) => void
  onEventClick: (event: Event) => void
}

export function WeekView({
  currentDate,
  events,
  categories,
  selectedCategoryId,
  onDateClick,
  onEventClick,
}: WeekViewProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll to 8 AM on mount
    if (scrollContainerRef.current) {
      const hourHeight = 48 // h-12 = 48px
      scrollContainerRef.current.scrollTop = hourHeight * 8
    }
  }, [])

  const getWeekDays = (date: Date) => {
    const startOfWeek = new Date(date)
    startOfWeek.setDate(date.getDate() - date.getDay())

    const days = []
    for (let i = 0; i < 7; i++) {
      const day = new Date(startOfWeek)
      day.setDate(startOfWeek.getDate() + i)
      days.push(day)
    }
    return days
  }

  const getEventsForDateAndHour = (date: Date, hour: number) => {
    return events.filter((event) => {
      const eventDate = new Date(event.start_time)
      const eventHour = eventDate.getHours()
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear() &&
        eventHour === hour
      )
    })
  }

  const isEventVisible = (event: Event) => {
    return selectedCategoryId === null || event.category_id === selectedCategoryId
  }

  const getCategoryColor = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.color || "#6366f1"
  }

  const weekDays = getWeekDays(currentDate)
  const today = new Date()
  const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

  const isToday = (date: Date) => {
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const hours = Array.from({ length: 24 }, (_, i) => i)

  return (
    <div className="flex flex-col h-full">
      {/* Week days header */}
      <div className="grid grid-cols-8 gap-2 p-4 border-b">
        <div /> {/* Empty cell for time column */}
        {weekDays.map((day, index) => (
          <div
            key={day.toISOString()}
            className={cn(
              "text-center",
              isToday(day) && "text-purple-400 font-bold"
            )}
          >
            <div className="text-sm font-semibold">{daysOfWeek[index]}</div>
            <div
              className={cn(
                "text-2xl mt-1",
                isToday(day)
                  ? "bg-purple-600 text-white rounded-full w-10 h-10 flex items-center justify-center mx-auto"
                  : ""
              )}
            >
              {day.getDate()}
            </div>
          </div>
        ))}
      </div>

      {/* Week grid */}
      <ScrollArea className="flex-1">
        <div ref={scrollContainerRef} className="p-4">
          <div className="grid grid-cols-8 gap-2 min-w-[800px]">
            {/* Time column */}
            <div>
              {hours.map((hour) => (
                <div key={hour} className="text-xs text-muted-foreground h-12 flex items-start">
                  {hour === 0
                    ? "12 AM"
                    : hour < 12
                    ? `${hour} AM`
                    : hour === 12
                    ? "12 PM"
                    : `${hour - 12} PM`}
                </div>
              ))}
            </div>

            {/* Day columns */}
            {weekDays.map((day) => (
              <div key={day.toISOString()} className="">
                {hours.map((hour) => {
                  const hourEvents = getEventsForDateAndHour(day, hour)
                  return (
                    <div
                      key={hour}
                      onClick={() => onDateClick(day)}
                      className={cn(
                        "h-12 border-t border-border cursor-pointer hover:bg-accent/30 transition-colors relative"
                      )}
                    >
                      {hourEvents.map((event) => (
                        <div
                          key={event.id}
                          onClick={(e) => {
                            e.stopPropagation()
                            onEventClick(event)
                          }}
                          className={cn(
                            "absolute inset-x-1 top-0.5 p-1 rounded text-xs cursor-pointer transition-all duration-200",
                            isEventVisible(event)
                              ? "hover:opacity-80"
                              : "opacity-30 hover:opacity-50 grayscale"
                          )}
                          style={{
                            backgroundColor: getCategoryColor(event.category_id),
                          }}
                          title={event.title}
                        >
                          <div className="font-medium truncate">{event.title}</div>
                          <div className="text-xs opacity-90">
                            {new Date(event.start_time).toLocaleTimeString("en-US", {
                              hour: "numeric",
                              minute: "2-digit",
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
