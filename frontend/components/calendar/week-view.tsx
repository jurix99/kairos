"use client"

import { useRef, useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import type { Event, Category } from "@/lib/api"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useSettings } from "@/contexts/settings-context"
import { getDayName, formatTime, formatHour } from "@/lib/i18n"

interface WeekViewProps {
  currentDate: Date
  events: Event[]
  categories: Category[]
  selectedCategoryId: string | null
  onDateClick: (date: Date) => void
  onEventClick: (event: Event) => void
  onEventDrop?: (event: Event, newStartTime: Date) => void
  onTimeSlotClick?: (date: Date, hour: number) => void
}

export function WeekView({
  currentDate,
  events,
  categories,
  selectedCategoryId,
  onDateClick,
  onEventClick,
  onEventDrop,
  onTimeSlotClick,
}: WeekViewProps) {
  const { settings } = useSettings()
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const [draggedEvent, setDraggedEvent] = useState<Event | null>(null)
  const [hoveredSlot, setHoveredSlot] = useState<{ date: Date; hour: number } | null>(null)

  useEffect(() => {
    // Scroll to center on current time
    if (scrollContainerRef.current) {
      const now = new Date()
      const currentHour = now.getHours()
      
      // Always center on current time, regardless of the hour
      const hourHeight = 80 // h-20 = 80px (better for 15-min increments)
      // Center the current hour in the viewport (show ~3 hours before and after)
      const targetScrollTop = hourHeight * Math.max(0, currentHour - 3)
      
      scrollContainerRef.current.scrollTop = targetScrollTop
    }
  }, [])

  const getWeekDays = (date: Date) => {
    const startOfWeek = new Date(date)
    // Calculer le lundi de la semaine (1 = lundi, 0 = dimanche)
    const dayOfWeek = date.getDay()
    const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek // Si dimanche (0), reculer de 6 jours
    startOfWeek.setDate(date.getDate() + daysToMonday)

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
      
      // Only show event in the hour it starts (will extend to following hours visually)
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear() &&
        eventHour === hour
      )
    })
  }

  const getEventsForDay = (date: Date) => {
    return events.filter((event) => {
      const eventDate = new Date(event.start_time)
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear()
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
    // Build a group of all events that overlap with each other (transitive closure)
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
      
      // Safety check to prevent infinite loop
      if (eventGroup.size === currentSize) {
        changed = false
      }
    }
    
    if (eventGroup.size === 1) {
      return { columnIndex: 0, totalColumns: 1 }
    }
    
    // Sort all events in group by start time, then by ID for consistency
    const allEvents = Array.from(eventGroup).sort((a, b) => {
      const timeDiff = new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      if (timeDiff !== 0) return timeDiff
      // Compare IDs (handle both string and number types)
      return String(a.id).localeCompare(String(b.id))
    })
    
    // Assign columns using a greedy algorithm
    const columns: Event[][] = []
    
    for (const evt of allEvents) {
      // Find the first column where this event doesn't overlap with any existing event
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
      
      // If no suitable column found, create a new one
      if (!placed) {
        columns.push([evt])
      }
    }
    
    // Find which column this event is in
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
    
    // Calculate duration in minutes
    const durationMs = endDate.getTime() - startDate.getTime()
    const durationMinutes = Math.max(15, Math.ceil(durationMs / (60 * 1000))) // Minimum 15 minutes
    
    // Hour slot height is 80px (h-20)
    const hourHeightPx = 80
    
    // Calculate top position (percentage within the starting hour slot)
    const topPercent = (eventMinutes / 60) * 100
    
    // Calculate height in pixels based on duration
    // Subtract 2px for a small gap between consecutive events
    const heightPx = (durationMinutes / 60) * hourHeightPx - 2
    
    // Calculate horizontal position for overlapping events
    const { columnIndex, totalColumns } = getEventLayout(event, dayEvents)
    
    // Width and position calculations with proper spacing
    const gapPercent = 1 // 1% gap between columns
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

  const handleDragStart = (e: React.DragEvent, event: Event) => {
    setDraggedEvent(event)
    e.dataTransfer.effectAllowed = "move"
    // Create a custom drag image (transparent)
    const dragImage = document.createElement("div")
    dragImage.style.opacity = "0"
    document.body.appendChild(dragImage)
    e.dataTransfer.setDragImage(dragImage, 0, 0)
    setTimeout(() => document.body.removeChild(dragImage), 0)
  }

  const handleDragOver = (e: React.DragEvent, date: Date, hour: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = "move"
    setHoveredSlot({ date, hour })
  }

  const handleDragLeave = () => {
    setHoveredSlot(null)
  }

  const handleDrop = (e: React.DragEvent, date: Date, hour: number) => {
    e.preventDefault()
    if (draggedEvent && onEventDrop) {
      const newStartTime = new Date(date)
      newStartTime.setHours(hour, 0, 0, 0)
      onEventDrop(draggedEvent, newStartTime)
    }
    setDraggedEvent(null)
    setHoveredSlot(null)
  }

  const handleTimeSlotClick = (date: Date, hour: number) => {
    if (onTimeSlotClick) {
      onTimeSlotClick(date, hour)
    } else {
      onDateClick(date)
    }
  }

  const weekDays = getWeekDays(currentDate)
  const today = new Date()
  
  // Utiliser les paramètres pour la langue et le format d'heure
  const language = settings.profile.language
  const timeFormat = settings.calendar.timeFormat

  const isToday = (date: Date) => {
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const isSlotHovered = (date: Date, hour: number) => {
    if (!hoveredSlot) return false
    return (
      hoveredSlot.date.getDate() === date.getDate() &&
      hoveredSlot.date.getMonth() === date.getMonth() &&
      hoveredSlot.date.getFullYear() === date.getFullYear() &&
      hoveredSlot.hour === hour
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
            <div className="text-sm font-semibold">{getDayName(index, language)}</div>
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
          <div className="grid grid-cols-8 gap-2 min-w-[800px] overflow-visible">
            {/* Time column */}
            <div>
            {hours.map((hour) => (
              <div key={hour} className="text-xs text-muted-foreground h-20 flex items-start">
                {formatHour(hour, timeFormat)}
              </div>
            ))}
            </div>

            {/* Day columns */}
            {weekDays.map((day) => {
              const dayEvents = getEventsForDay(day)
              return (
                <div key={day.toISOString()} className="overflow-visible">
                  {hours.map((hour) => {
                    const hourEvents = getEventsForDateAndHour(day, hour)
                    const isHovered = isSlotHovered(day, hour)
                    return (
                    <div
                      key={hour}
                      onClick={() => handleTimeSlotClick(day, hour)}
                      onDragOver={(e) => handleDragOver(e, day, hour)}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => handleDrop(e, day, hour)}
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
                          {formatHour(hour, timeFormat)}
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
                          {formatTime(new Date(event.start_time), timeFormat, language)}
                        </div>
                          </div>
                        )
                      })}
                    </div>
                    )
                  })}
                </div>
              )
            })}
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
