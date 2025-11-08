"use client"

import { useEffect, useState } from "react"
import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { SiteHeader } from "@/components/site-header"
import { useAuth } from "@/contexts/auth-context"
import { useSettings } from "@/contexts/settings-context"
import { CategoryManager } from "@/components/category-manager"
import { CalendarIntegrationsManager } from "@/components/calendar-integrations-manager"
import { NotificationsBell } from "@/components/notifications-bell"
import { apiClient, type Category } from "@/lib/api"

export default function SettingsPage() {
  const { user } = useAuth()
  const {
    settings,
    updateSetting,
    updateNestedSetting,
    resetSettings: resetSettingsContext,
    saveSettings,
    hasUnsavedChanges
  } = useSettings()
  const [isLoading, setIsLoading] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [categoriesLoading, setCategoriesLoading] = useState(true)

  // Initialize settings with user data
  useEffect(() => {
    if (user && settings.profile.displayName !== user.name) {
      updateSetting('profile', 'displayName', user.name || '')
      updateSetting('profile', 'email', user.email || '')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  // Load categories
  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      setCategoriesLoading(true)
      const categoriesData = await apiClient.getCategories()
      setCategories(categoriesData)
    } catch (error) {
      console.error('Failed to load categories:', error)
    } finally {
      setCategoriesLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    setIsLoading(true)
    try {
      await saveSettings()
      alert('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleResetSettings = () => {
    const confirmed = confirm('Are you sure you want to reset all settings to default?')
    if (confirmed) {
      resetSettingsContext()
    }
  }

  return (
    <>
      <SiteHeader 
        user={user} 
        title="Settings" 
        icon={Settings}
        controls={
          <div className="flex items-center gap-2">
            {hasUnsavedChanges && (
              <Badge variant="secondary" className="mr-2">
                Unsaved changes
              </Badge>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleResetSettings}
              disabled={isLoading}
            >
              Reset
            </Button>
            <Button
              size="sm"
              onClick={handleSaveSettings}
              disabled={!hasUnsavedChanges || isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        }
      />
      
      <div className="flex flex-1 flex-col">
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          
          {/* Profile Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>
                Manage your account information and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="displayName">Display Name</Label>
                  <Input
                    id="displayName"
                    value={settings.profile.displayName}
                    onChange={(e) => updateSetting('profile', 'displayName', e.target.value)}
                    placeholder="Your display name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.profile.email}
                    onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                    placeholder="your.email@example.com"
                    disabled
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select
                    value={settings.profile.timezone}
                    onValueChange={(value) => updateSetting('profile', 'timezone', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Europe/Paris">Europe/Paris (GMT+1)</SelectItem>
                      <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                      <SelectItem value="America/New_York">America/New_York (GMT-5)</SelectItem>
                      <SelectItem value="America/Los_Angeles">America/Los_Angeles (GMT-8)</SelectItem>
                      <SelectItem value="Asia/Tokyo">Asia/Tokyo (GMT+9)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={settings.profile.language}
                    onValueChange={(value) => updateSetting('profile', 'language', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notifications Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>
                Configure how and when you want to be notified
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="emailNotifications">Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications via email
                  </p>
                </div>
                <Switch
                  id="emailNotifications"
                  checked={settings.notifications.emailNotifications}
                  onCheckedChange={(checked) => updateSetting('notifications', 'emailNotifications', checked)}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="eventReminders">Event Reminders</Label>
                  <p className="text-sm text-muted-foreground">
                    Get reminded before your events
                  </p>
                </div>
                <Switch
                  id="eventReminders"
                  checked={settings.notifications.eventReminders}
                  onCheckedChange={(checked) => updateSetting('notifications', 'eventReminders', checked)}
                />
              </div>
              
              {settings.notifications.eventReminders && (
                <div className="space-y-2 ml-4">
                  <Label htmlFor="reminderMinutes">Reminder Time</Label>
                  <Select
                    value={settings.notifications.reminderMinutes.toString()}
                    onValueChange={(value) => updateSetting('notifications', 'reminderMinutes', parseInt(value))}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">5 minutes before</SelectItem>
                      <SelectItem value="15">15 minutes before</SelectItem>
                      <SelectItem value="30">30 minutes before</SelectItem>
                      <SelectItem value="60">1 hour before</SelectItem>
                      <SelectItem value="1440">1 day before</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="weeklyDigest">Weekly Digest</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive a weekly summary of your activities
                  </p>
                </div>
                <Switch
                  id="weeklyDigest"
                  checked={settings.notifications.weeklyDigest}
                  onCheckedChange={(checked) => updateSetting('notifications', 'weeklyDigest', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Calendar Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Calendar</CardTitle>
              <CardDescription>
                Customize your calendar view and behavior
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="defaultView">Default View</Label>
                  <Select
                    value={settings.calendar.defaultView}
                    onValueChange={(value) => updateSetting('calendar', 'defaultView', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="month">Month View</SelectItem>
                      <SelectItem value="week">Week View</SelectItem>
                      <SelectItem value="day">Day View</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weekStartsOn">Week Starts On</Label>
                  <Select
                    value={settings.calendar.weekStartsOn}
                    onValueChange={(value) => updateSetting('calendar', 'weekStartsOn', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sunday">Sunday</SelectItem>
                      <SelectItem value="monday">Monday</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="timeFormat">Time Format</Label>
                  <Select
                    value={settings.calendar.timeFormat}
                    onValueChange={(value) => updateSetting('calendar', 'timeFormat', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="12h">12-hour (AM/PM)</SelectItem>
                      <SelectItem value="24h">24-hour</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div></div> {/* Empty cell for grid layout */}
              </div>
              
              <div className="space-y-2">
                <Label>Working Hours</Label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="workStart" className="text-sm">Start</Label>
                    <Input
                      id="workStart"
                      type="time"
                      value={settings.calendar.workingHours.start}
                      onChange={(e) => updateNestedSetting('calendar', 'workingHours', 'start', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="workEnd" className="text-sm">End</Label>
                    <Input
                      id="workEnd"
                      type="time"
                      value={settings.calendar.workingHours.end}
                      onChange={(e) => updateNestedSetting('calendar', 'workingHours', 'end', e.target.value)}
                    />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="showWeekends">Show Weekends</Label>
                  <p className="text-sm text-muted-foreground">
                    Display Saturday and Sunday in calendar views
                  </p>
                </div>
                <Switch
                  id="showWeekends"
                  checked={settings.calendar.showWeekends}
                  onCheckedChange={(checked) => updateSetting('calendar', 'showWeekends', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Appearance Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>
                Customize the look and feel of your application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme">Theme</Label>
                <Select
                  value={settings.appearance.theme}
                  onValueChange={(value) => updateSetting('appearance', 'theme', value)}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="compactMode">Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Use a more compact layout to fit more information
                  </p>
                </div>
                <Switch
                  id="compactMode"
                  checked={settings.appearance.compactMode}
                  onCheckedChange={(checked) => updateSetting('appearance', 'compactMode', checked)}
                />
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="showEventColors">Show Event Colors</Label>
                  <p className="text-sm text-muted-foreground">
                    Display category colors on events
                  </p>
                </div>
                <Switch
                  id="showEventColors"
                  checked={settings.appearance.showEventColors}
                  onCheckedChange={(checked) => updateSetting('appearance', 'showEventColors', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Categories Management */}
          <CategoryManager 
            categories={categories}
            onCategoriesChange={loadCategories}
          />

          {/* Calendar Integrations */}
          <CalendarIntegrationsManager 
            onIntegrationsChange={loadCategories}
          />

        </div>
      </div>
      <NotificationsBell categories={categories} />
    </>
  )
}
