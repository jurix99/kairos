"use client"

import { useState } from "react"
import { Check, Palette } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { DEFAULT_CATEGORY_COLORS, isValidHexColor, getContrastColor } from "@/lib/colors"

interface ColorPickerProps {
  color: string
  onColorChange: (color: string) => void
  label?: string
}

export function ColorPicker({ color, onColorChange, label }: ColorPickerProps) {
  const [customColor, setCustomColor] = useState(color)
  const [open, setOpen] = useState(false)

  const handleColorSelect = (selectedColor: string) => {
    onColorChange(selectedColor)
    setCustomColor(selectedColor)
    setOpen(false)
  }

  const handleCustomColorChange = (value: string) => {
    setCustomColor(value)
    if (isValidHexColor(value)) {
      onColorChange(value)
    }
  }

  return (
    <div className="space-y-2">
      {label && <Label>{label}</Label>}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="w-full justify-start"
            size="sm"
          >
            <div
              className="w-4 h-4 rounded-full mr-2"
              style={{ backgroundColor: color }}
            />
            <span className="flex-1 text-left">{color}</span>
            <Palette className="w-4 h-4 ml-2" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-64 p-3">
          <div className="space-y-3">
            <div>
              <Label className="text-sm font-medium">Couleurs prédéfinies</Label>
              <div className="grid grid-cols-8 gap-2 mt-2">
                {DEFAULT_CATEGORY_COLORS.map((presetColor) => (
                  <button
                    key={presetColor}
                    onClick={() => handleColorSelect(presetColor)}
                    className={cn(
                      "w-8 h-8 rounded-full border-2 transition-all duration-200 hover:scale-110",
                      color === presetColor
                        ? "border-foreground ring-2 ring-offset-2 ring-foreground"
                        : "border-border hover:border-foreground"
                    )}
                    style={{ backgroundColor: presetColor }}
                    title={presetColor}
                  >
                    {color === presetColor && (
                      <Check 
                        className="w-4 h-4 mx-auto" 
                        style={{ color: getContrastColor(presetColor) }}
                      />
                    )}
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <Label htmlFor="custom-color" className="text-sm font-medium">
                Couleur personnalisée
              </Label>
              <div className="flex gap-2 mt-2">
                <Input
                  id="custom-color"
                  value={customColor}
                  onChange={(e) => handleCustomColorChange(e.target.value)}
                  placeholder="#000000"
                  className="flex-1"
                />
                <input
                  type="color"
                  value={color}
                  onChange={(e) => handleColorSelect(e.target.value)}
                  className="w-12 h-10 rounded border border-input cursor-pointer"
                />
              </div>
              {customColor && !isValidHexColor(customColor) && (
                <p className="text-xs text-destructive mt-1">
                  Format invalide. Utilisez le format #RRGGBB
                </p>
              )}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}