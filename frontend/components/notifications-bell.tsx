"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Bell, X, Check, Clock } from "lucide-react"
import { apiClient } from "@/lib/api"
import type { Event, Category } from "@/lib/api"
import { useSettings } from "@/contexts/settings-context"
import { formatTime } from "@/lib/i18n"

const isToday = (date: Date): boolean => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const isBefore = (date: Date, compareDate: Date): boolean => {
  return date.getTime() < compareDate.getTime()
}

interface NotificationsBellProps {
  categories: Category[]
}

export function NotificationsBell({ categories }: NotificationsBellProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [pastEvents, setPastEvents] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { settings } = useSettings()

  // Récupérer les événements passés de la journée
  const fetchPastEvents = async () => {
    try {
      setIsLoading(true)
      // Load only today's events for notifications
      const now = new Date()
      const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999)
      
      const allEvents = await apiClient.getEvents(startOfDay, endOfDay)
      
      // Filtrer les événements passés de la journée qui ne sont pas encore "completed" ou "cancelled"
      const todayPastEvents = allEvents.filter(event => {
        const eventEnd = new Date(event.end_time)
        return (
          isToday(eventEnd) && 
          isBefore(eventEnd, now) && 
          event.status !== 'completed' && 
          event.status !== 'cancelled'
        )
      })
      
      setPastEvents(todayPastEvents)
    } catch (error) {
      console.error("Failed to fetch past events:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // Charger les événements passés au montage du composant
  useEffect(() => {
    fetchPastEvents()
    
    // Recharger toutes les 5 minutes
    const interval = setInterval(fetchPastEvents, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  // Marquer un événement comme complété
  const markAsCompleted = async (eventId: string) => {
    try {
      await apiClient.updateEvent(eventId, { status: 'completed' })
      setPastEvents(prev => prev.filter(event => event.id !== eventId))
    } catch (error) {
      console.error("Failed to mark event as completed:", error)
    }
  }

  // Marquer un événement comme non réalisé (cancelled)
  const markAsNotDone = async (eventId: string) => {
    try {
      await apiClient.updateEvent(eventId, { status: 'cancelled' })
      setPastEvents(prev => prev.filter(event => event.id !== eventId))
    } catch (error) {
      console.error("Failed to mark event as not done:", error)
    }
  }

  // Trouver la catégorie d'un événement
  const getCategoryForEvent = (event: Event) => {
    return categories.find(cat => cat.id === event.category_id)
  }

  // Obtenir le nombre d'événements passés non traités
  const pastEventsCount = pastEvents.length

  return (
    <>
      {/* Bouton flottant en bas à droite */}
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="relative rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all duration-200"
          variant={pastEventsCount > 0 ? "default" : "outline"}
        >
          <Bell className="h-6 w-6" />
          {pastEventsCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0 flex items-center justify-center text-xs"
            >
              {pastEventsCount > 9 ? '9+' : pastEventsCount}
            </Badge>
          )}
        </Button>
      </div>

      {/* Dialog des notifications */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Événements passés aujourd'hui
            </DialogTitle>
          </DialogHeader>
          
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : pastEvents.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucun événement passé aujourd'hui</p>
                <p className="text-sm">Tous vos événements sont à jour !</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pastEvents.map((event) => {
                  const category = getCategoryForEvent(event)
                  return (
                    <div
                      key={event.id}
                      className="border rounded-lg p-4 space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {category && (
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: category.color }}
                              />
                            )}
                            <h4 className="font-medium">{event.title}</h4>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {formatTime(new Date(event.start_time), settings.calendar.timeFormat, settings.profile.language)} - 
                            {formatTime(new Date(event.end_time), settings.calendar.timeFormat, settings.profile.language)}
                          </p>
                          {event.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {event.description}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          onClick={() => markAsCompleted(event.id)}
                          size="sm"
                          className="flex-1 gap-2"
                        >
                          <Check className="h-4 w-4" />
                          Réalisé
                        </Button>
                        <Button
                          onClick={() => markAsNotDone(event.id)}
                          variant="outline"
                          size="sm"
                          className="flex-1 gap-2"
                        >
                          <X className="h-4 w-4" />
                          Pas fait
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
