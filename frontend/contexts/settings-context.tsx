"use client"

import React, { createContext, useContext, useState, useEffect } from 'react'

// Settings data structure
export interface SettingsData {
  profile: {
    displayName: string
    email: string
    timezone: string
    language: string
  }
  notifications: {
    emailNotifications: boolean
    eventReminders: boolean
    weeklyDigest: boolean
    reminderMinutes: number
  }
  calendar: {
    defaultView: 'month' | 'week' | 'day'
    weekStartsOn: 'sunday' | 'monday'
    workingHours: {
      start: string
      end: string
    }
    showWeekends: boolean
    timeFormat: '12h' | '24h'
  }
  appearance: {
    theme: 'light' | 'dark' | 'system'
    compactMode: boolean
    showEventColors: boolean
  }
}

const defaultSettings: SettingsData = {
  profile: {
    displayName: '',
    email: '',
    timezone: 'Europe/Paris',
    language: 'en'
  },
  notifications: {
    emailNotifications: true,
    eventReminders: true,
    weeklyDigest: false,
    reminderMinutes: 15
  },
  calendar: {
    defaultView: 'month',
    weekStartsOn: 'monday',
    workingHours: {
      start: '09:00',
      end: '18:00'
    },
    showWeekends: true,
    timeFormat: '12h'
  },
  appearance: {
    theme: 'dark',
    compactMode: false,
    showEventColors: true // Enable by default
  }
}

interface SettingsContextType {
  settings: SettingsData
  updateSetting: (section: keyof SettingsData, key: string, value: any) => void
  updateNestedSetting: (section: keyof SettingsData, nestedKey: string, key: string, value: any) => void
  resetSettings: () => void
  saveSettings: () => Promise<void>
  hasUnsavedChanges: boolean
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<SettingsData>(defaultSettings)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('kairos-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...defaultSettings, ...parsed })
      } catch (error) {
        console.error('Failed to parse saved settings:', error)
      }
    }
  }, [])

  const updateSetting = (section: keyof SettingsData, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
    setHasUnsavedChanges(true)
  }

  const updateNestedSetting = (section: keyof SettingsData, nestedKey: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [nestedKey]: {
          ...(prev[section] as any)[nestedKey],
          [key]: value
        }
      }
    }))
    setHasUnsavedChanges(true)
  }

  const resetSettings = () => {
    setSettings(defaultSettings)
    setHasUnsavedChanges(true)
  }

  const saveSettings = async () => {
    try {
      // Save to localStorage
      localStorage.setItem('kairos-settings', JSON.stringify(settings))
      
      // Here you would typically save to backend
      // await apiClient.updateUserSettings(settings)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setHasUnsavedChanges(false)
      return Promise.resolve()
    } catch (error) {
      console.error('Failed to save settings:', error)
      throw error
    }
  }

  return (
    <SettingsContext.Provider value={{
      settings,
      updateSetting,
      updateNestedSetting,
      resetSettings,
      saveSettings,
      hasUnsavedChanges
    }}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}
