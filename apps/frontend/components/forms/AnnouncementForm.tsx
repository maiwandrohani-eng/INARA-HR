'use client'

import { useState } from 'react'
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
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Megaphone } from 'lucide-react'

interface AnnouncementFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function AnnouncementForm({ open, onOpenChange, onSubmitSuccess }: AnnouncementFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [announcementType, setAnnouncementType] = useState('general')
  const [targetAudience, setTargetAudience] = useState('all')
  const [priority, setPriority] = useState('normal')
  const [expiresAt, setExpiresAt] = useState('')

  const resetForm = () => {
    setTitle('')
    setContent('')
    setAnnouncementType('general')
    setTargetAudience('all')
    setPriority('normal')
    setExpiresAt('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const announcementData = {
        title,
        content,
        announcement_type: announcementType,
        target_audience: targetAudience,
        priority,
        expires_at: expiresAt || null,
      }

      await apiClient.post('/notifications/announcements', announcementData)

      toast({
        title: 'Success',
        description: 'Announcement created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating announcement:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create announcement',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Megaphone className="h-6 w-6" />
            Create Announcement
          </DialogTitle>
          <DialogDescription>
            Broadcast an announcement to employees
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Announcement title"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="content">Content *</Label>
            <Textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Announcement content"
              rows={6}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="announcement-type">Type</Label>
              <Select value={announcementType} onValueChange={setAnnouncementType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="policy">Policy</SelectItem>
                  <SelectItem value="event">Event</SelectItem>
                  <SelectItem value="update">Update</SelectItem>
                  <SelectItem value="reminder">Reminder</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="target-audience">Target Audience</Label>
              <Select value={targetAudience} onValueChange={setTargetAudience}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Employees</SelectItem>
                  <SelectItem value="department">Department</SelectItem>
                  <SelectItem value="role">Role</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="expires-at">Expires At (Optional)</Label>
            <Input
              id="expires-at"
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select value={priority} onValueChange={setPriority}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="normal">Normal</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Announcement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

