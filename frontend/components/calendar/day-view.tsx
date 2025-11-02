"use client"

import { useRef, useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import type { Event, Category } from "@/lib/api"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { useSettings } from "@/contexts/settings-context"

interface DayViewProps {
  currentDate: Date
  events: Event[]
  categories: Category[]
  selectedCategoryId: string | null
  onEventClick: (event: Event) => void
  onEventDrop?: (event: Event, newStartTime: Date) => void
  onTimeSlotClick?: (date: Date, hour: number) => void
}

export function DayView({
  currentDate,
  events,
  categories,
  selectedCategoryId,
  onEventClick,
  onEventDrop,
  onTimeSlotClick,
}: DayViewProps) {
  const { settings } = useSettings()
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [draggedEvent, setDraggedEvent] = useState<Event | null>(null)
  const [hoveredSlot, setHoveredSlot] = useState<number | null>(null)

  useEffect(() => {
    // Scroll to center on current time
    const timer = setTimeout(() => {
      if (scrollContainerRef.current) {
        const now = new Date()
        const currentHour = now.getHours()
        
        // Always center on current time, regardless of the hour
        const hourHeight = 80 // h-20 = 80px
        // Center the current hour in the viewport (show ~3 hours before and after)
        const targetScrollTop = hourHeight * Math.max(0, currentHour - 3)
        
        // Find the scrollable viewport (ScrollArea creates a nested structure)
        const viewport = scrollContainerRef.current.parentElement?.querySelector('[data-radix-scroll-area-viewport]')
        if (viewport) {
          viewport.scrollTop = targetScrollTop
        } else {
          scrollContainerRef.current.scrollTop = targetScrollTop
        }
      }
    }, 100) // Small delay to ensure ScrollArea is fully initialized
    
    return () => clearTimeout(timer)
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

  const getEventsForHour = (date: Date, hour: number) => {
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

  const eventsOverlap = (event1: Event, event2: Event): boolean => {
    const start1 = new Date(event1.start_time).getTime()
    const end1 = new Date(event1.end_time).getTime()
    const start2 = new Date(event2.start_time).getTime()
    const end2 = new Date(event2.end_time).getTime()
    
    return start1 < end2 && start2 < end1
  }

  const getEventLayout = (event: Event, dayEvents: Event[]) => {
    const eventGroup = new Set<Event>([event])
    let changed = true
    
    while (changed) {
      changed = false
      const currentSize = eventGroup.size
      
      for (const e1 of eventGroup) {
        for (const e2 of dayEvents) {
          if (!eventGroup.has(e2) && eventsOverlap(e1, e2)) {
            eventGroup.add(e2)
            changed = true
          }
        }
      }
      
      if (eventGroup.size === currentSize) {
        changed = false
      }
    }
    
    if (eventGroup.size === 1) {
      return { columnIndex: 0, totalColumns: 1 }
    }
    
    const allEvents = Array.from(eventGroup).sort((a, b) => {
      const timeDiff = new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      if (timeDiff !== 0) return timeDiff
      return String(a.id).localeCompare(String(b.id))
    })
    
    const columns: Event[][] = []
    
    for (const evt of allEvents) {
      let placed = false
      for (let i = 0; i < columns.length; i++) {
        const columnEvents = columns[i]
        const hasOverlap = columnEvents.some(colEvt => eventsOverlap(evt, colEvt))
        
        if (!hasOverlap) {
          columns[i].push(evt)
          placed = true
          break
        }
      }
      
      if (!placed) {
        columns.push([evt])
      }
    }
    
    let columnIndex = 0
    for (let i = 0; i < columns.length; i++) {
      if (columns[i].find(e => e.id === event.id)) {
        columnIndex = i
        break
      }
    }
    
    const totalColumns = columns.length
    
    return { columnIndex, totalColumns }
  }

  const getEventPosition = (event: Event, dayEvents: Event[]) => {
    const startDate = new Date(event.start_time)
    const endDate = new Date(event.end_time)
    const eventMinutes = startDate.getMinutes()
    
    const durationMs = endDate.getTime() - startDate.getTime()
    const durationMinutes = Math.max(15, Math.ceil(durationMs / (60 * 1000)))
    
    const hourHeightPx = 80
    const topPercent = (eventMinutes / 60) * 100
    const heightPx = (durationMinutes / 60) * hourHeightPx - 2
    
    const { columnIndex, totalColumns } = getEventLayout(event, dayEvents)
    
    const gapPercent = 1
    const availableWidth = 100 - (totalColumns - 1) * gapPercent
    const widthPercent = availableWidth / totalColumns
    const leftPercent = columnIndex * (widthPercent + gapPercent)
    
    return {
      top: `${topPercent}%`,
      height: `${heightPx}px`,
      width: `${widthPercent}%`,
      left: `${leftPercent}%`,
    }
  }

  const handleDragStart = (e: React.DragEvent, event: Event) => {
    setDraggedEvent(event)
    e.dataTransfer.effectAllowed = "move"
    const dragImage = document.createElement("div")
    dragImage.style.opacity = "0"
    document.body.appendChild(dragImage)
    e.dataTransfer.setDragImage(dragImage, 0, 0)
    setTimeout(() => document.body.removeChild(dragImage), 0)
  }

  const handleDragOver = (e: React.DragEvent, hour: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = "move"
    setHoveredSlot(hour)
  }

  const handleDragLeave = () => {
    setHoveredSlot(null)
  }

  const handleDrop = (e: React.DragEvent, hour: number) => {
    e.preventDefault()
    if (draggedEvent && onEventDrop) {
      const newStartTime = new Date(currentDate)
      newStartTime.setHours(hour, 0, 0, 0)
      onEventDrop(draggedEvent, newStartTime)
    }
    setDraggedEvent(null)
    setHoveredSlot(null)
  }

  const handleTimeSlotClick = (hour: number) => {
    if (onTimeSlotClick) {
      onTimeSlotClick(currentDate, hour)
    }
  }

  const isEventVisible = (event: Event) => {
    return selectedCategoryId === null || event.category_id === selectedCategoryId
  }

  const getCategoryColor = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.color || "#6366f1"
  }

  const getEventBackgroundColor = (event: Event) => {
    if (!settings.appearance.showEventColors) {
      return "#6b7280" // neutral gray when colors are disabled
    }
    return getCategoryColor(event.category_id)
  }

  const getCategoryName = (categoryId: string) => {
    const category = categories.find((c) => c.id === categoryId)
    return category?.name || "Unknown"
  }

  const dayEvents = getEventsForDate(currentDate)
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const now = new Date()
  const currentHour = now.getHours()

  return (
    <div className="flex flex-col h-full">
      {/* Day header - optimized horizontal layout */}
      <div className="p-3 border-b">
        <div className="flex items-center justify-center gap-3">
          <div className="text-lg font-semibold text-muted-foreground">
            {currentDate.toLocaleDateString("en-US", { weekday: "long" })}
          </div>
          <div className="text-3xl font-bold">{currentDate.getDate()}</div>
          <div className="text-lg text-muted-foreground">
            {currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-2 gap-4 p-4 min-h-0">
        {/* Timeline view */}
        <div className="flex flex-col min-h-0">
          <h3 className="text-sm font-semibold mb-2 flex-shrink-0">Timeline</h3>
          <ScrollArea className="flex-1 border rounded-lg">
            <div className="p-2" ref={scrollContainerRef}>
              <div className="grid grid-cols-[80px_1fr] gap-2 min-w-[400px] overflow-visible">
                {/* Time column */}
                <div>
                  {hours.map((hour) => (
                    <div 
                      key={hour} 
                      className="text-xs text-muted-foreground h-20 flex items-start px-1 relative"
                    >
                      {hour === currentHour && (
                        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-purple-500"></div>
                      )}
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

                {/* Events column */}
                <div className="overflow-visible">
                  {hours.map((hour) => {
                    const hourEvents = getEventsForHour(currentDate, hour)
                    const isHovered = hoveredSlot === hour
                    return (
                      <div
                        key={hour}
                        onClick={() => handleTimeSlotClick(hour)}
                        onDragOver={(e) => handleDragOver(e, hour)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, hour)}
                      className={cn(
                        "h-20 border-t border-border cursor-pointer hover:bg-accent/30 transition-colors relative overflow-visible",
                        isHovered && draggedEvent && "bg-purple-500/20 border-purple-500 border-2 ring-2 ring-purple-500/50"
                      )}
                      >
                        {/* 15-minute guide lines */}
                        <div className="absolute top-1/4 left-0 right-0 h-px bg-border/30 pointer-events-none" />
                        <div className="absolute top-1/2 left-0 right-0 h-px bg-border/50 pointer-events-none" />
                        <div className="absolute top-3/4 left-0 right-0 h-px bg-border/30 pointer-events-none" />
                        
                        {/* Show preview of dragged event in hovered slot */}
                        {isHovered && draggedEvent && (
                          <div
                            className="absolute inset-x-1 top-0.5 p-1 rounded text-xs pointer-events-none animate-pulse border-2 border-purple-500"
                            style={{
                              backgroundColor: getEventBackgroundColor(draggedEvent),
                              opacity: 0.7,
                            }}
                          >
                            <div className="font-medium truncate">{draggedEvent.title}</div>
                            <div className="text-xs opacity-90">
                              {hour === 0
                                ? "12:00 AM"
                                : hour < 12
                                ? `${hour}:00 AM`
                                : hour === 12
                                ? "12:00 PM"
                                : `${hour - 12}:00 PM`}
                            </div>
                          </div>
                        )}
                        
                        {hourEvents.map((event) => {
                          const position = getEventPosition(event, dayEvents)
                          return (
                            <div
                              key={event.id}
                              draggable={true}
                              onDragStart={(e) => handleDragStart(e, event)}
                              onClick={(e) => {
                                e.stopPropagation()
                                onEventClick(event)
                              }}
                              className={cn(
                                "absolute p-1 rounded text-xs cursor-move transition-all duration-200 overflow-hidden z-10",
                                isEventVisible(event)
                                  ? "hover:opacity-80 hover:shadow-lg hover:z-20"
                                  : "opacity-30 hover:opacity-50 grayscale",
                                draggedEvent?.id === event.id && "opacity-20 cursor-grabbing"
                              )}
                              style={{
                                backgroundColor: getEventBackgroundColor(event),
                                top: position.top,
                                height: position.height,
                                width: position.width,
                                left: position.left,
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
                          )
                        })}
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </ScrollArea>
        </div>

        {/* Events list */}
        <div className="flex flex-col min-h-0">
          <h3 className="text-sm font-semibold mb-2 flex-shrink-0">
            Events ({dayEvents.filter(isEventVisible).length})
          </h3>
          <ScrollArea className="flex-1 border rounded-lg">
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
                              borderColor: settings.appearance.showEventColors 
                                ? getCategoryColor(event.category_id) 
                                : "#6b7280",
                              color: settings.appearance.showEventColors 
                                ? getCategoryColor(event.category_id) 
                                : "#6b7280",
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
                          backgroundColor: getEventBackgroundColor(event),
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
