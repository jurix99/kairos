"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Clock } from "lucide-react"
import { cn } from "@/lib/utils"

interface TimePickerProps {
  value?: string // Format: HH:mm
  onChange: (time: string) => void
  label?: string
  placeholder?: string
  className?: string
  disabled?: boolean
  required?: boolean
}

export function TimePicker({
  value = "",
  onChange,
  label,
  placeholder = "Select time",
  className,
  disabled = false,
  required = false,
}: TimePickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [hours, setHours] = useState("")
  const [minutes, setMinutes] = useState("")

  // Parse value when it changes
  useEffect(() => {
    if (value) {
      const [h, m] = value.split(":")
      setHours(h || "")
      setMinutes(m || "")
    } else {
      setHours("")
      setMinutes("")
    }
  }, [value])

  const handleTimeChange = (newHours: string, newMinutes: string) => {
    const formattedTime = `${newHours.padStart(2, "0")}:${newMinutes.padStart(2, "0")}`
    onChange(formattedTime)
  }

  const handleHoursChange = (newHours: string) => {
    const numHours = parseInt(newHours)
    if (isNaN(numHours) || numHours < 0 || numHours > 23) return
    setHours(newHours)
    handleTimeChange(newHours, minutes || "00")
  }

  const handleMinutesChange = (newMinutes: string) => {
    const numMinutes = parseInt(newMinutes)
    if (isNaN(numMinutes) || numMinutes < 0 || numMinutes > 59) return
    setMinutes(newMinutes)
    handleTimeChange(hours || "00", newMinutes)
  }

  const getDisplayValue = () => {
    if (value) {
      return value
    }
    return placeholder
  }

  // Quick time options - More comprehensive and better organized
  const quickTimes = [
    // Morning
    { label: "8:00", value: "08:00", category: "morning" },
    { label: "8:30", value: "08:30", category: "morning" },
    { label: "9:00", value: "09:00", category: "morning" },
    { label: "9:30", value: "09:30", category: "morning" },
    { label: "10:00", value: "10:00", category: "morning" },
    { label: "10:30", value: "10:30", category: "morning" },
    { label: "11:00", value: "11:00", category: "morning" },
    { label: "11:30", value: "11:30", category: "morning" },
    // Afternoon
    { label: "12:00", value: "12:00", category: "afternoon" },
    { label: "12:30", value: "12:30", category: "afternoon" },
    { label: "13:00", value: "13:00", category: "afternoon" },
    { label: "13:30", value: "13:30", category: "afternoon" },
    { label: "14:00", value: "14:00", category: "afternoon" },
    { label: "14:30", value: "14:30", category: "afternoon" },
    { label: "15:00", value: "15:00", category: "afternoon" },
    { label: "15:30", value: "15:30", category: "afternoon" },
    { label: "16:00", value: "16:00", category: "afternoon" },
    { label: "16:30", value: "16:30", category: "afternoon" },
    { label: "17:00", value: "17:00", category: "afternoon" },
    { label: "17:30", value: "17:30", category: "afternoon" },
    // Evening
    { label: "18:00", value: "18:00", category: "evening" },
    { label: "18:30", value: "18:30", category: "evening" },
    { label: "19:00", value: "19:00", category: "evening" },
    { label: "19:30", value: "19:30", category: "evening" },
    { label: "20:00", value: "20:00", category: "evening" },
    { label: "20:30", value: "20:30", category: "evening" },
  ]

  const morningTimes = quickTimes.filter(t => t.category === "morning")
  const afternoonTimes = quickTimes.filter(t => t.category === "afternoon")
  const eveningTimes = quickTimes.filter(t => t.category === "evening")

  return (
    <div className={cn("grid gap-2", className)}>
      {label && (
        <Label>
          {label} {required && <span className="text-destructive">*</span>}
        </Label>
      )}
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal",
              !value && "text-muted-foreground"
            )}
            disabled={disabled}
          >
            <Clock className="mr-2 h-4 w-4" />
            {getDisplayValue()}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-4" align="start">
          <div className="space-y-4">
            {/* Manual time input */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="hours" className="text-xs">Heures</Label>
                <Input
                  id="hours"
                  type="number"
                  min="0"
                  max="23"
                  value={hours}
                  onChange={(e) => handleHoursChange(e.target.value)}
                  placeholder="HH"
                  className="text-center"
                />
              </div>
              <div>
                <Label htmlFor="minutes" className="text-xs">Minutes</Label>
                <Input
                  id="minutes"
                  type="number"
                  min="0"
                  max="59"
                  step="5"
                  value={minutes}
                  onChange={(e) => handleMinutesChange(e.target.value)}
                  placeholder="MM"
                  className="text-center"
                />
              </div>
            </div>

            {/* Quick time buttons - organized by categories */}
            <div>
              <Label className="text-xs mb-2 block">Sélection rapide</Label>
              
              {/* Morning */}
              <div className="mb-3">
                <p className="text-xs text-muted-foreground mb-1">Matin</p>
                <div className="grid grid-cols-4 gap-1">
                  {morningTimes.map((time) => (
                    <Button
                      key={time.value}
                      variant={value === time.value ? "default" : "outline"}
                      size="sm"
                      className="text-xs h-7"
                      onClick={() => {
                        onChange(time.value)
                        setIsOpen(false)
                      }}
                    >
                      {time.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Afternoon */}
              <div className="mb-3">
                <p className="text-xs text-muted-foreground mb-1">Après-midi</p>
                <div className="grid grid-cols-4 gap-1">
                  {afternoonTimes.map((time) => (
                    <Button
                      key={time.value}
                      variant={value === time.value ? "default" : "outline"}
                      size="sm"
                      className="text-xs h-7"
                      onClick={() => {
                        onChange(time.value)
                        setIsOpen(false)
                      }}
                    >
                      {time.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Evening */}
              <div className="mb-3">
                <p className="text-xs text-muted-foreground mb-1">Soirée</p>
                <div className="grid grid-cols-4 gap-1">
                  {eveningTimes.map((time) => (
                    <Button
                      key={time.value}
                      variant={value === time.value ? "default" : "outline"}
                      size="sm"
                      className="text-xs h-7"
                      onClick={() => {
                        onChange(time.value)
                        setIsOpen(false)
                      }}
                    >
                      {time.label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* Clear button */}
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() => {
                onChange("")
                setIsOpen(false)
              }}
            >
              Clear
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
