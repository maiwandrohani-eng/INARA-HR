'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Settings, Save, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface SystemSettings {
  organization_name: string
  organization_email: string
  organization_phone?: string
  default_currency: string
  default_timezone: string
  date_format: string
  time_format: string
  week_start_day: string
  password_expiry_days: number
  session_timeout_minutes: number
  enable_two_factor: boolean
  enable_email_notifications: boolean
  enable_sms_notifications: boolean
  max_login_attempts: number
  lockout_duration_minutes: number
}

interface SystemSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SystemSettingsDialog({ open, onOpenChange }: SystemSettingsDialogProps) {
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('')
  
  // Form state
  const [orgName, setOrgName] = useState('INARA')
  const [orgEmail, setOrgEmail] = useState('admin@inara.org')
  const [orgPhone, setOrgPhone] = useState('')
  const [defaultCurrency, setDefaultCurrency] = useState('USD')
  const [defaultTimezone, setDefaultTimezone] = useState('UTC')
  const [dateFormat, setDateFormat] = useState('YYYY-MM-DD')
  const [timeFormat, setTimeFormat] = useState('24h')
  const [weekStartDay, setWeekStartDay] = useState('monday')
  const [passwordExpiryDays, setPasswordExpiryDays] = useState('90')
  const [sessionTimeoutMinutes, setSessionTimeoutMinutes] = useState('60')
  const [enableTwoFactor, setEnableTwoFactor] = useState(false)
  const [enableEmailNotifications, setEnableEmailNotifications] = useState(true)
  const [enableSmsNotifications, setEnableSmsNotifications] = useState(false)
  const [maxLoginAttempts, setMaxLoginAttempts] = useState('5')
  const [lockoutDuration, setLockoutDuration] = useState('30')

  useEffect(() => {
    if (open) {
      fetchSettings()
    }
  }, [open])

  const fetchSettings = async () => {
    setLoading(true)
    setMessage('')
    
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/admin/settings', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Populate form with fetched data
        if (data.organization_name) setOrgName(data.organization_name)
        if (data.organization_email) setOrgEmail(data.organization_email)
        if (data.organization_phone) setOrgPhone(data.organization_phone)
        if (data.default_currency) setDefaultCurrency(data.default_currency)
        if (data.default_timezone) setDefaultTimezone(data.default_timezone)
        if (data.date_format) setDateFormat(data.date_format)
        if (data.time_format) setTimeFormat(data.time_format)
        if (data.week_start_day) setWeekStartDay(data.week_start_day)
        if (data.password_expiry_days) setPasswordExpiryDays(data.password_expiry_days.toString())
        if (data.session_timeout_minutes) setSessionTimeoutMinutes(data.session_timeout_minutes.toString())
        if (data.enable_two_factor !== undefined) setEnableTwoFactor(data.enable_two_factor)
        if (data.enable_email_notifications !== undefined) setEnableEmailNotifications(data.enable_email_notifications)
        if (data.enable_sms_notifications !== undefined) setEnableSmsNotifications(data.enable_sms_notifications)
        if (data.max_login_attempts) setMaxLoginAttempts(data.max_login_attempts.toString())
        if (data.lockout_duration_minutes) setLockoutDuration(data.lockout_duration_minutes.toString())
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    
    try {
      const settingsData = {
        organization_name: orgName,
        organization_email: orgEmail,
        organization_phone: orgPhone || null,
        default_currency: defaultCurrency,
        default_timezone: defaultTimezone,
        date_format: dateFormat,
        time_format: timeFormat,
        week_start_day: weekStartDay,
        password_expiry_days: parseInt(passwordExpiryDays),
        session_timeout_minutes: parseInt(sessionTimeoutMinutes),
        enable_two_factor: enableTwoFactor,
        enable_email_notifications: enableEmailNotifications,
        enable_sms_notifications: enableSmsNotifications,
        max_login_attempts: parseInt(maxLoginAttempts),
        lockout_duration_minutes: parseInt(lockoutDuration),
      }

      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('Not authenticated. Please log in again.')
      }

      console.log('Saving settings:', settingsData)
      
      const response = await fetch('http://localhost:8000/api/v1/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(settingsData),
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        const contentType = response.headers.get('content-type')
        let errorMessage = 'Failed to save settings'
        
        try {
          if (contentType && contentType.includes('application/json')) {
            const error = await response.json()
            errorMessage = error.detail || error.message || errorMessage
          } else {
            const text = await response.text()
            errorMessage = text || errorMessage
          }
        } catch (e) {
          console.error('Error parsing error response:', e)
        }
        
        console.error('Save settings failed:', response.status, errorMessage)
        throw new Error(errorMessage)
      }

      const result = await response.json()
      console.log('Settings saved successfully:', result)
      
      setMessage('System settings saved successfully!')
      setMessageType('success')
    } catch (error) {
      console.error('Error saving settings:', error)
      setMessage(`Failed to save settings: ${error instanceof Error ? error.message : 'Please try again'}`)
      setMessageType('error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Settings className="h-6 w-6" />
            System Settings
          </DialogTitle>
          <DialogDescription>
            Configure system-wide preferences and security settings
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {message && (
            <Alert variant={messageType === 'error' ? 'destructive' : 'default'}>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          {loading ? (
            <div className="p-8 text-center text-gray-500">
              Loading settings...
            </div>
          ) : (
            <div className="space-y-6">
              {/* Organization Settings */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">Organization Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="org-name">Organization Name *</Label>
                    <Input
                      id="org-name"
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="org-email">Organization Email *</Label>
                    <Input
                      id="org-email"
                      type="email"
                      value={orgEmail}
                      onChange={(e) => setOrgEmail(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="org-phone">Organization Phone</Label>
                    <Input
                      id="org-phone"
                      type="tel"
                      value={orgPhone}
                      onChange={(e) => setOrgPhone(e.target.value)}
                      placeholder="+1 234 567 8900"
                    />
                  </div>
                </div>
              </div>

              {/* Regional Settings */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">Regional Settings</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="currency">Default Currency</Label>
                    <Select value={defaultCurrency} onValueChange={setDefaultCurrency}>
                      <SelectTrigger id="currency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="USD">USD - US Dollar</SelectItem>
                        <SelectItem value="EUR">EUR - Euro</SelectItem>
                        <SelectItem value="GBP">GBP - British Pound</SelectItem>
                        <SelectItem value="TRY">TRY - Turkish Lira</SelectItem>
                        <SelectItem value="LBP">LBP - Lebanese Pound</SelectItem>
                        <SelectItem value="JOD">JOD - Jordanian Dinar</SelectItem>
                        <SelectItem value="EGP">EGP - Egyptian Pound</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Default Timezone</Label>
                    <Select value={defaultTimezone} onValueChange={setDefaultTimezone}>
                      <SelectTrigger id="timezone">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC">UTC</SelectItem>
                        <SelectItem value="Europe/London">Europe/London</SelectItem>
                        <SelectItem value="Europe/Istanbul">Europe/Istanbul</SelectItem>
                        <SelectItem value="Asia/Beirut">Asia/Beirut</SelectItem>
                        <SelectItem value="Asia/Damascus">Asia/Damascus</SelectItem>
                        <SelectItem value="Asia/Baghdad">Asia/Baghdad</SelectItem>
                        <SelectItem value="Asia/Kabul">Asia/Kabul</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="date-format">Date Format</Label>
                    <Select value={dateFormat} onValueChange={setDateFormat}>
                      <SelectTrigger id="date-format">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="YYYY-MM-DD">YYYY-MM-DD (2024-12-07)</SelectItem>
                        <SelectItem value="DD/MM/YYYY">DD/MM/YYYY (07/12/2024)</SelectItem>
                        <SelectItem value="MM/DD/YYYY">MM/DD/YYYY (12/07/2024)</SelectItem>
                        <SelectItem value="DD-MMM-YYYY">DD-MMM-YYYY (07-Dec-2024)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="time-format">Time Format</Label>
                    <Select value={timeFormat} onValueChange={setTimeFormat}>
                      <SelectTrigger id="time-format">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="24h">24 Hour (13:00)</SelectItem>
                        <SelectItem value="12h">12 Hour (1:00 PM)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="week-start">Week Start Day</Label>
                    <Select value={weekStartDay} onValueChange={setWeekStartDay}>
                      <SelectTrigger id="week-start">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sunday">Sunday</SelectItem>
                        <SelectItem value="monday">Monday</SelectItem>
                        <SelectItem value="saturday">Saturday</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Security Settings */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password-expiry">Password Expiry (days)</Label>
                    <Input
                      id="password-expiry"
                      type="number"
                      value={passwordExpiryDays}
                      onChange={(e) => setPasswordExpiryDays(e.target.value)}
                      min="0"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="session-timeout">Session Timeout (minutes)</Label>
                    <Input
                      id="session-timeout"
                      type="number"
                      value={sessionTimeoutMinutes}
                      onChange={(e) => setSessionTimeoutMinutes(e.target.value)}
                      min="5"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="max-attempts">Max Login Attempts</Label>
                    <Input
                      id="max-attempts"
                      type="number"
                      value={maxLoginAttempts}
                      onChange={(e) => setMaxLoginAttempts(e.target.value)}
                      min="3"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lockout-duration">Lockout Duration (minutes)</Label>
                    <Input
                      id="lockout-duration"
                      type="number"
                      value={lockoutDuration}
                      onChange={(e) => setLockoutDuration(e.target.value)}
                      min="5"
                    />
                  </div>

                  <div className="flex items-center justify-between col-span-2 p-3 bg-gray-50 rounded">
                    <Label htmlFor="two-factor">Enable Two-Factor Authentication</Label>
                    <Switch
                      id="two-factor"
                      checked={enableTwoFactor}
                      onCheckedChange={setEnableTwoFactor}
                    />
                  </div>
                </div>
              </div>

              {/* Notification Settings */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-4">Notification Settings</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <Label htmlFor="email-notifications">Enable Email Notifications</Label>
                    <Switch
                      id="email-notifications"
                      checked={enableEmailNotifications}
                      onCheckedChange={setEnableEmailNotifications}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <Label htmlFor="sms-notifications">Enable SMS Notifications</Label>
                    <Switch
                      id="sms-notifications"
                      checked={enableSmsNotifications}
                      onCheckedChange={setEnableSmsNotifications}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || loading}>
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
