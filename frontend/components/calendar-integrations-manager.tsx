"use client"

import { useState, useEffect } from "react"
import { Plus, RefreshCw, Trash2, Calendar, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { apiClient, type CalendarIntegration, type CalendarIntegrationCreate, type SyncResult } from "@/lib/api"

interface CalendarIntegrationsManagerProps {
  onIntegrationsChange?: () => void
}

export function CalendarIntegrationsManager({ onIntegrationsChange }: CalendarIntegrationsManagerProps) {
  const [integrations, setIntegrations] = useState<CalendarIntegration[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isSyncing, setIsSyncing] = useState<number | null>(null)
  const [syncResults, setSyncResults] = useState<{ [key: number]: SyncResult }>({})
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<CalendarIntegrationCreate>({
    provider: 'apple',
    calendar_url: '',
    calendar_name: '',
    username: '',
    password: '',
    sync_enabled: true,
  })

  useEffect(() => {
    loadIntegrations()
  }, [])

  const loadIntegrations = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getIntegrations()
      setIntegrations(data)
    } catch (error) {
      console.error('Failed to load integrations:', error)
      setError('Failed to load calendar integrations')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateIntegration = async () => {
    try {
      setError(null)
      await apiClient.createIntegration(formData)
      setIsDialogOpen(false)
      setFormData({
        provider: 'apple',
        calendar_url: '',
        calendar_name: '',
        username: '',
        password: '',
        sync_enabled: true,
      })
      await loadIntegrations()
      if (onIntegrationsChange) {
        onIntegrationsChange()
      }
    } catch (error: any) {
      console.error('Failed to create integration:', error)
      setError(error.message || 'Failed to create integration')
    }
  }

  const handleDeleteIntegration = async (id: number) => {
    if (!confirm('Are you sure you want to remove this calendar integration?')) {
      return
    }

    try {
      await apiClient.deleteIntegration(id)
      await loadIntegrations()
      if (onIntegrationsChange) {
        onIntegrationsChange()
      }
    } catch (error) {
      console.error('Failed to delete integration:', error)
      setError('Failed to delete integration')
    }
  }

  const handleSyncIntegration = async (id: number) => {
    try {
      setIsSyncing(id)
      setError(null)
      const result = await apiClient.syncIntegration(id)
      setSyncResults({ ...syncResults, [id]: result })
      await loadIntegrations()
      if (onIntegrationsChange) {
        onIntegrationsChange()
      }
    } catch (error: any) {
      console.error('Failed to sync integration:', error)
      setError(error.message || 'Failed to sync calendar')
    } finally {
      setIsSyncing(null)
    }
  }

  const handleToggleSync = async (integration: CalendarIntegration) => {
    try {
      await apiClient.updateIntegration(integration.id, {
        sync_enabled: !integration.sync_enabled,
      })
      await loadIntegrations()
    } catch (error) {
      console.error('Failed to update integration:', error)
      setError('Failed to update sync settings')
    }
  }

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'apple':
        return '🍎'
      case 'google':
        return '📅'
      case 'outlook':
        return '📧'
      default:
        return '📆'
    }
  }

  const formatLastSync = (dateString?: string) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hours ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} days ago`
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Calendar Integrations</CardTitle>
            <CardDescription>
              Connect external calendars to sync events automatically
            </CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add Integration
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Add Calendar Integration</DialogTitle>
                <DialogDescription>
                  Connect your Apple Calendar, Google Calendar, or Outlook Calendar
                </DialogDescription>
              </DialogHeader>
              
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="provider">Provider</Label>
                  <Select
                    value={formData.provider}
                    onValueChange={(value) => setFormData({ ...formData, provider: value as 'apple' | 'google' | 'outlook' })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="apple">🍎 Apple Calendar (iCloud)</SelectItem>
                      <SelectItem value="google">📅 Google Calendar</SelectItem>
                      <SelectItem value="outlook">📧 Outlook Calendar</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="calendar_name">Calendar Name (Optional)</Label>
                  <Input
                    id="calendar_name"
                    value={formData.calendar_name}
                    onChange={(e) => setFormData({ ...formData, calendar_name: e.target.value })}
                    placeholder="My Work Calendar"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="calendar_url">Calendar URL</Label>
                  <Input
                    id="calendar_url"
                    value={formData.calendar_url}
                    onChange={(e) => setFormData({ ...formData, calendar_url: e.target.value })}
                    placeholder="https://caldav.icloud.com/..."
                  />
                  <p className="text-xs text-muted-foreground">
                    For Apple Calendar: Go to iCloud.com → Calendar → Share → Copy CalDAV URL
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="username">Username/Email</Label>
                  <Input
                    id="username"
                    type="email"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="your.email@icloud.com"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="App-specific password"
                  />
                  <p className="text-xs text-muted-foreground">
                    For Apple: Create an app-specific password in your Apple ID settings
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="sync_enabled"
                    checked={formData.sync_enabled}
                    onCheckedChange={(checked) => setFormData({ ...formData, sync_enabled: checked })}
                  />
                  <Label htmlFor="sync_enabled">Enable automatic sync</Label>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateIntegration}>
                  Add Integration
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : integrations.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Calendar className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <p>No calendar integrations yet</p>
            <p className="text-sm">Click "Add Integration" to connect your first calendar</p>
          </div>
        ) : (
          <div className="space-y-4">
            {integrations.map((integration) => (
              <div
                key={integration.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="text-3xl">
                    {getProviderIcon(integration.provider)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">
                        {integration.calendar_name || `${integration.provider.charAt(0).toUpperCase() + integration.provider.slice(1)} Calendar`}
                      </h4>
                      {integration.is_active ? (
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          <CheckCircle className="mr-1 h-3 w-3" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-red-600 border-red-600">
                          <XCircle className="mr-1 h-3 w-3" />
                          Inactive
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {integration.username}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Last sync: {formatLastSync(integration.last_sync)}
                    </p>
                    {syncResults[integration.id] && (
                      <p className="text-xs text-green-600 mt-1">
                        ✓ {syncResults[integration.id].message}
                        {syncResults[integration.id].events_imported > 0 && (
                          <span> ({syncResults[integration.id].events_imported} events imported)</span>
                        )}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-2 mr-2">
                    <Switch
                      checked={integration.sync_enabled}
                      onCheckedChange={() => handleToggleSync(integration)}
                    />
                    <span className="text-xs text-muted-foreground">
                      {integration.sync_enabled ? 'Sync On' : 'Sync Off'}
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleSyncIntegration(integration.id)}
                    disabled={isSyncing === integration.id}
                  >
                    {isSyncing === integration.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteIntegration(integration.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
