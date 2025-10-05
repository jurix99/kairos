"use client"

import { useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import type { Event, Category } from "@/lib/api"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"

interface DayViewProps {
  currentDate: Date
  events: Event[]
  categories: Category[]
  selectedCategoryId: string | null
  onEventClick: (event: Event) => void
}

export function DayView({
  currentDate,
  events,
  categories,
  selectedCategoryId,
  onEventClick,
}: DayViewProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll to 8 AM on mount
    if (scrollContainerRef.current) {
      const hourHeight = 80 // h-20 = 80px
      scrollContainerRef.current.scrollTop = hourHeight * 8
    }
  }, [currentDate])

  const getEventsForDate = (date: Date) => {
    return events
      .filter((event) => {
        const eventDate = new Date(event.start_time)
        return (
          eventDate.getDate() === date.getDate() &&
          eventDate.getMonth() === date.getMonth() &&
          eventDate.getFullYear() === date.getFullYear()
        )
      })
      .sort(
        (a, b) =>
          new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      )
  }

  const isEventVisible = (event: Event) => {
    return selectedCategoryId === null || event.category_id === selectedCategoryId
  }

  const getCategoryColor = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.color || "#6366f1"
  }

  const getCategoryName = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.name || "Unknown"
  }

  const dayEvents = getEventsForDate(currentDate)
  const hours = Array.from({ length: 24 }, (_, i) => i)

  return (
    <div className="flex flex-col h-full">
      {/* Day header */}
      <div className="p-4 border-b">
        <div className="text-center">
          <div className="text-sm font-semibold text-muted-foreground">
            {currentDate.toLocaleDateString("en-US", { weekday: "long" })}
          </div>
          <div className="text-4xl font-bold mt-1">{currentDate.getDate()}</div>
          <div className="text-sm text-muted-foreground">
            {currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
        {/* Timeline view */}
        <div className="h-full">
          <h3 className="text-sm font-semibold mb-2">Timeline</h3>
          <ScrollArea className="h-full border rounded-lg">
            <div ref={scrollContainerRef} className="p-2">
              {hours.map((hour) => {
                const hourEvents = dayEvents.filter((event) => {
                  const eventHour = new Date(event.start_time).getHours()
                  return eventHour === hour
                })

                return (
                  <div key={hour} className="flex gap-2 min-h-[80px] border-t border-border">
                    <div className="w-20 flex-shrink-0 text-xs text-muted-foreground pt-1">
                      {hour === 0
                        ? "12 AM"
                        : hour < 12
                        ? `${hour} AM`
                        : hour === 12
                        ? "12 PM"
                        : `${hour - 12} PM`}
                    </div>
                    <div className="flex-1 py-1 space-y-1">
                      {hourEvents.map((event) => (
                        <div
                          key={event.id}
                          onClick={() => onEventClick(event)}
                          className={cn(
                            "p-2 rounded-lg cursor-pointer transition-all duration-200 border",
                            isEventVisible(event)
                              ? "hover:opacity-80"
                              : "opacity-30 hover:opacity-50 grayscale"
                          )}
                          style={{
                            backgroundColor: getCategoryColor(event.category_id),
                            borderColor: getCategoryColor(event.category_id),
                          }}
                        >
                          <div className="font-medium text-sm">{event.title}</div>
                          <div className="text-xs opacity-90 mt-1">
                            {new Date(event.start_time).toLocaleTimeString("en-US", {
                              hour: "numeric",
                              minute: "2-digit",
                            })}{" "}
                            -{" "}
                            {new Date(event.end_time).toLocaleTimeString("en-US", {
                              hour: "numeric",
                              minute: "2-digit",
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </ScrollArea>
        </div>

        {/* Events list */}
        <div className="h-full">
          <h3 className="text-sm font-semibold mb-2">
            Events ({dayEvents.filter(isEventVisible).length})
          </h3>
          <ScrollArea className="h-full border rounded-lg">
            <div className="p-4 space-y-3">
              {dayEvents.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No events for this day
                </div>
              ) : (
                dayEvents.map((event) => (
                  <div
                    key={event.id}
                    onClick={() => onEventClick(event)}
                    className={cn(
                      "p-4 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md",
                      isEventVisible(event)
                        ? "bg-card hover:bg-accent/50"
                        : "opacity-30 hover:opacity-50 grayscale"
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="font-semibold">{event.title}</div>
                        {event.description && (
                          <div className="text-sm text-muted-foreground mt-1">
                            {event.description}
                          </div>
                        )}
                        <div className="flex items-center gap-2 mt-2">
                          <Badge
                            variant="outline"
                            className="text-xs"
                            style={{
                              borderColor: getCategoryColor(event.category_id),
                              color: getCategoryColor(event.category_id),
                            }}
                          >
                            {getCategoryName(event.category_id)}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(event.start_time).toLocaleTimeString("en-US", {
                              hour: "numeric",
                              minute: "2-digit",
                            })}{" "}
                            -{" "}
                            {new Date(event.end_time).toLocaleTimeString("en-US", {
                              hour: "numeric",
                              minute: "2-digit",
                            })}
                          </span>
                        </div>
                      </div>
                      <div
                        className="w-1 h-full rounded-full flex-shrink-0"
                        style={{
                          backgroundColor: getCategoryColor(event.category_id),
                        }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>
  )
}
