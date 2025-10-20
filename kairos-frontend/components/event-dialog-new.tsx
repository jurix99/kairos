"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { DateTimePicker } from "@/components/ui/datetime-picker"
import { RecurrencePicker, type RecurrenceRule } from "@/components/ui/recurrence-picker"
import { apiClient } from "@/lib/api"
import type { Event, Category } from "@/lib/api"
import { CalendarPlus, Loader2 } from "lucide-react"

interface EventDialogProps {
  categories: Category[]
  onEventCreated?: () => void
  trigger?: React.ReactNode
  defaultDate?: Date
  defaultStartTime?: Date
  defaultEndTime?: Date
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function EventDialog({
  categories,
  onEventCreated,
  trigger,
  defaultDate = new Date(),
  defaultStartTime,
  defaultEndTime,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
}: EventDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen
  const setOpen = controlledOnOpenChange || setInternalOpen

  const getInitialStartTime = () => {
    if (defaultStartTime) return formatDateTimeLocal(defaultStartTime)
    return formatDateTimeLocal(defaultDate)
  }

  const getInitialEndTime = () => {
    if (defaultEndTime) return formatDateTimeLocal(defaultEndTime)
    if (defaultStartTime) return formatDateTimeLocal(new Date(defaultStartTime.getTime() + 60 * 60 * 1000))
    return formatDateTimeLocal(new Date(defaultDate.getTime() + 60 * 60 * 1000))
  }

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category_id: "",
    start_time: "",
    end_time: "",
    priority: "medium",
    status: "pending",
    location: "",
    recurrence: null as RecurrenceRule | null,
  })

  function formatDateTimeLocal(date: Date): string {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, "0")
    const day = String(date.getDate()).padStart(2, "0")
    const hours = String(date.getHours()).padStart(2, "0")
    const minutes = String(date.getMinutes()).padStart(2, "0")
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }

  // Update form data when default times change
  useEffect(() => {
    if (open) {
      setFormData({
        title: "",
        description: "",
        category_id: "",
        start_time: getInitialStartTime(),
        end_time: getInitialEndTime(),
        priority: "medium",
        status: "pending",
        location: "",
        recurrence: null,
      })
    }
  }, [open, defaultStartTime, defaultEndTime])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title || !formData.category_id || !formData.start_time || !formData.end_time) {
      alert("Please fill in all required fields")
      return
    }

    try {
      setIsLoading(true)
      await apiClient.createEvent({
        title: formData.title,
        description: formData.description,
        category_id: formData.category_id,
        start_time: formData.start_time,
        end_time: formData.end_time,
        location: formData.location,
        priority: formData.priority as "low" | "medium" | "high",
        status: formData.status as "pending" | "in_progress" | "completed" | "cancelled",
        recurrence: formData.recurrence,
      })

      // Reset form
      setFormData({
        title: "",
        description: "",
        category_id: "",
        start_time: formatDateTimeLocal(new Date()),
        end_time: formatDateTimeLocal(new Date(Date.now() + 60 * 60 * 1000)),
        priority: "medium",
        status: "pending",
        location: "",
        recurrence: null,
      })

      setOpen(false)
      onEventCreated?.()
    } catch (error) {
      console.error("Failed to create event:", error)
      alert("Failed to create event. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const hasCategories = categories.length > 0

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="gap-2" disabled={!hasCategories}>
            <CalendarPlus className="h-4 w-4" />
            Add Event
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New Event</DialogTitle>
            <DialogDescription>
              Add a new event to your calendar. Fill in the details below.
            </DialogDescription>
          </DialogHeader>
          
          {!hasCategories && (
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 my-4">
              <p className="text-sm text-yellow-500">
                You need to create at least one category before adding events.
              </p>
            </div>
          )}
          
          <div className="grid gap-4 py-4">
            {/* Title */}
            <div className="grid gap-2">
              <Label htmlFor="title">
                Title <span className="text-destructive">*</span>
              </Label>
              <Input
                id="title"
                placeholder="Event title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>

            {/* Description */}
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Event description (optional)"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>

            {/* Category */}
            <div className="grid gap-2">
              <Label htmlFor="category">
                Category <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.category_id}
                onValueChange={(value) => setFormData({ ...formData, category_id: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
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
            </div>

            {/* Start and End Time */}
            <DateTimePicker
              label="Start Time"
              value={formData.start_time}
              onChange={(datetime) => setFormData({ ...formData, start_time: datetime })}
              required
            />

            <DateTimePicker
              label="End Time"
              value={formData.end_time}
              onChange={(datetime) => setFormData({ ...formData, end_time: datetime })}
              required
              min={formData.start_time}
            />

            {/* Location */}
            <div className="grid gap-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="Event location (optional)"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>

            {/* Priority and Status */}
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="priority">Priority</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(value) => setFormData({ ...formData, priority: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Recurrence Section */}
          <RecurrencePicker
            value={formData.recurrence}
            onChange={(recurrence) => setFormData({ ...formData, recurrence })}
          />

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Event"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

