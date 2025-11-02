"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar, Repeat } from "lucide-react"
import { cn } from "@/lib/utils"

export interface RecurrenceRule {
  type: "daily" | "weekly" | "monthly" | "yearly"
  interval: number
  daysOfWeek?: number[]
  endDate?: string
  count?: number
}

interface RecurrencePickerProps {
  value?: RecurrenceRule | null
  onChange: (recurrence: RecurrenceRule | null) => void
  className?: string
}

const DAYS_OF_WEEK = [
  { label: "Lun", value: 0 },
  { label: "Mar", value: 1 },
  { label: "Mer", value: 2 },
  { label: "Jeu", value: 3 },
  { label: "Ven", value: 4 },
  { label: "Sam", value: 5 },
  { label: "Dim", value: 6 },
]

export function RecurrencePicker({
  value,
  onChange,
  className,
}: RecurrencePickerProps) {
  const [isEnabled, setIsEnabled] = useState(!!value)

  const handleEnabledChange = (enabled: boolean) => {
    setIsEnabled(enabled)
    if (!enabled) {
      onChange(null)
    } else {
      // Set default recurrence
      onChange({
        type: "weekly",
        interval: 1,
      })
    }
  }

  const handleRecurrenceChange = (field: keyof RecurrenceRule, newValue: any) => {
    if (!value) return
    
    const updatedRecurrence = { ...value, [field]: newValue }
    
    // Clear daysOfWeek if not daily
    if (field === "type" && newValue !== "daily") {
      delete updatedRecurrence.daysOfWeek
    }
    
    onChange(updatedRecurrence)
  }

  const handleDayToggle = (day: number) => {
    if (!value) return
    
    const currentDays = value.daysOfWeek || []
    const newDays = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day].sort()
    
    handleRecurrenceChange("daysOfWeek", newDays.length > 0 ? newDays : undefined)
  }

  const formatDateForInput = (date: Date): string => {
    return date.toISOString().split('T')[0]
  }

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Repeat className="h-4 w-4" />
          Récurrence
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Enable/Disable Toggle */}
        <div className="flex items-center justify-between">
          <Label htmlFor="recurrence-enabled" className="text-sm font-medium">
            Répéter cet événement
          </Label>
          <Switch
            id="recurrence-enabled"
            checked={isEnabled}
            onCheckedChange={handleEnabledChange}
          />
        </div>

        {isEnabled && value && (
          <div className="space-y-4 border-t pt-4">
            {/* Recurrence Type */}
            <div className="grid gap-2">
              <Label className="text-sm">Type de récurrence</Label>
              <Select
                value={value.type}
                onValueChange={(type) => handleRecurrenceChange("type", type)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Quotidien</SelectItem>
                  <SelectItem value="weekly">Hebdomadaire</SelectItem>
                  <SelectItem value="monthly">Mensuel</SelectItem>
                  <SelectItem value="yearly">Annuel</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Interval */}
            <div className="grid gap-2">
              <Label className="text-sm">
                Répéter tous les{" "}
                <Input
                  type="number"
                  min="1"
                  max="365"
                  value={value.interval}
                  onChange={(e) => handleRecurrenceChange("interval", parseInt(e.target.value) || 1)}
                  className="inline-block w-16 h-8 text-center mx-1"
                />
                {value.type === "daily" && (value.daysOfWeek?.length ? "semaines" : "jours")}
                {value.type === "weekly" && "semaines"}
                {value.type === "monthly" && "mois"}
                {value.type === "yearly" && "années"}
              </Label>
            </div>

            {/* Days of Week (for daily recurrence) */}
            {value.type === "daily" && (
              <div className="grid gap-2">
                <Label className="text-sm">Jours de la semaine</Label>
                <div className="flex gap-1">
                  {DAYS_OF_WEEK.map((day) => (
                    <Button
                      key={day.value}
                      type="button"
                      variant={
                        value.daysOfWeek?.includes(day.value) ? "default" : "outline"
                      }
                      size="sm"
                      className="w-12 h-8 text-xs"
                      onClick={() => handleDayToggle(day.value)}
                    >
                      {day.label}
                    </Button>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  Laissez vide pour tous les jours
                </p>
              </div>
            )}

            {/* End Condition */}
            <div className="grid gap-2">
              <Label className="text-sm">Fin de récurrence</Label>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="end-date" className="text-xs">Date de fin (optionnel)</Label>
                  <Input
                    id="end-date"
                    type="date"
                    value={value.endDate || ""}
                    onChange={(e) => {
                      if (e.target.value) {
                        handleRecurrenceChange("count", undefined)
                      }
                      handleRecurrenceChange("endDate", e.target.value || undefined)
                    }}
                    min={formatDateForInput(new Date())}
                  />
                </div>
                <div className="text-center text-xs text-muted-foreground">— ou —</div>
                <div>
                  <Label htmlFor="occurrence-count" className="text-xs">Nombre d'occurrences (optionnel)</Label>
                  <Input
                    id="occurrence-count"
                    type="number"
                    min="1"
                    max="1000"
                    value={value.count || ""}
                    onChange={(e) => {
                      if (e.target.value) {
                        handleRecurrenceChange("endDate", undefined)
                      }
                      handleRecurrenceChange("count", e.target.value ? parseInt(e.target.value) : undefined)
                    }}
                    placeholder="Illimité"
                  />
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Spécifiez soit une date de fin, soit un nombre d'occurrences (ou laissez vide pour une récurrence infinie)
              </p>
            </div>

            {/* Preview */}
            <div className="bg-muted/50 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Aperçu :</p>
              <p className="text-sm">
                {value.type === "daily" && value.daysOfWeek?.length ? (
                  <>
                    Chaque {DAYS_OF_WEEK.filter(d => value.daysOfWeek?.includes(d.value)).map(d => d.label).join(", ")}
                    {value.interval > 1 && ` (toutes les ${value.interval} semaines)`}
                  </>
                ) : (
                  <>
                    {value.type === "daily" && `Tous les ${value.interval === 1 ? "" : value.interval + " "}jours`}
                    {value.type === "weekly" && `Toutes les ${value.interval === 1 ? "" : value.interval + " "}semaines`}
                    {value.type === "monthly" && `Tous les ${value.interval === 1 ? "" : value.interval + " "}mois`}
                    {value.type === "yearly" && `Toutes les ${value.interval === 1 ? "" : value.interval + " "}années`}
                  </>
                )}
                
                {value.endDate && ` jusqu'au ${new Date(value.endDate).toLocaleDateString("fr-FR")}`}
                {value.count && ` pour ${value.count} occurrences`}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
