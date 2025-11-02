"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { TimePicker } from "@/components/ui/time-picker"
import { cn } from "@/lib/utils"

interface DateTimePickerProps {
  label?: string
  value?: string // ISO datetime string
  onChange: (datetime: string) => void
  className?: string
  disabled?: boolean
  required?: boolean
  min?: string
  max?: string
}

export function DateTimePicker({
  label,
  value = "",
  onChange,
  className,
  disabled = false,
  required = false,
  min,
  max,
}: DateTimePickerProps) {
  const [date, setDate] = useState("")
  const [time, setTime] = useState("")

  // Parse datetime value into date and time
  useEffect(() => {
    console.log(`🔍 DateTimePicker received value: ${value}`)
    if (value) {
      // Traiter à la fois les formats ISO avec timezone et sans timezone
      let datetime: Date
      if (value.includes('T') && !value.includes('Z') && !value.includes('+')) {
        // Format local déjà (2025-10-11T18:00:00)
        datetime = new Date(value)
      } else {
        // Format ISO avec timezone
        datetime = new Date(value)
      }
      
      if (!isNaN(datetime.getTime())) {
        const dateStr = datetime.toISOString().split('T')[0]
        const timeStr = datetime.toTimeString().slice(0, 5)
        console.log(`🔍 Parsed to date: ${dateStr}, time: ${timeStr}`)
        setDate(dateStr)
        setTime(timeStr)
      }
    } else {
      setDate("")
      setTime("")
    }
  }, [value])

  const handleDateChange = (newDate: string) => {
    setDate(newDate)
    updateDateTime(newDate, time)
  }

  const handleTimeChange = (newTime: string) => {
    setTime(newTime)
    updateDateTime(date, newTime)
  }

  const updateDateTime = (dateValue: string, timeValue: string) => {
    if (dateValue && timeValue) {
      // Créer une date locale sans conversion UTC
      const datetime = new Date(`${dateValue}T${timeValue}`)
      if (!isNaN(datetime.getTime())) {
        // Utiliser toLocaleDateTimeString pour préserver l'heure locale
        const year = datetime.getFullYear()
        const month = String(datetime.getMonth() + 1).padStart(2, "0")
        const day = String(datetime.getDate()).padStart(2, "0")
        const hours = String(datetime.getHours()).padStart(2, "0")
        const minutes = String(datetime.getMinutes()).padStart(2, "0")
        const localISOString = `${year}-${month}-${day}T${hours}:${minutes}:00`
        
        console.log(`🔄 DateTimePicker: Local time ${timeValue} preserved as ${localISOString}`)
        onChange(localISOString)
      }
    } else if (dateValue) {
      // If only date is provided, use current time or 09:00
      const defaultTime = timeValue || "09:00"
      const datetime = new Date(`${dateValue}T${defaultTime}`)
      if (!isNaN(datetime.getTime())) {
        const year = datetime.getFullYear()
        const month = String(datetime.getMonth() + 1).padStart(2, "0")
        const day = String(datetime.getDate()).padStart(2, "0")
        const hours = String(datetime.getHours()).padStart(2, "0")
        const minutes = String(datetime.getMinutes()).padStart(2, "0")
        const localISOString = `${year}-${month}-${day}T${hours}:${minutes}:00`
        
        console.log(`🔄 DateTimePicker: Default time preserved as ${localISOString}`)
        onChange(localISOString)
      }
    }
  }

  const getMinDate = () => {
    if (min) {
      return new Date(min).toISOString().split('T')[0]
    }
    return undefined
  }

  const getMaxDate = () => {
    if (max) {
      return new Date(max).toISOString().split('T')[0]
    }
    return undefined
  }

  return (
    <div className={cn("grid gap-2", className)}>
      {label && (
        <Label>
          {label} {required && <span className="text-destructive">*</span>}
        </Label>
      )}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label htmlFor={`${label?.toLowerCase().replace(/\s+/g, '-') || 'date'}-date`} className="text-xs text-muted-foreground">
            Date
          </Label>
          <Input
            id={`${label?.toLowerCase().replace(/\s+/g, '-') || 'date'}-date`}
            type="date"
            value={date}
            onChange={(e) => handleDateChange(e.target.value)}
            disabled={disabled}
            required={required}
            min={getMinDate()}
            max={getMaxDate()}
          />
        </div>
        <div>
          <TimePicker
            value={time}
            onChange={handleTimeChange}
            label=""
            placeholder="Heure"
            disabled={disabled}
            className="mt-[20px]" // Align with date input
          />
        </div>
      </div>
    </div>
  )
}
