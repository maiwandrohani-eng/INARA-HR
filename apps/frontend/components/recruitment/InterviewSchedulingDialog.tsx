'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api-client'
import { useEmployees } from '@/hooks/useEmployees'

interface InterviewSchedulingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  applicationId: string
  applicationName: string
  onSuccess?: () => void
}

export function InterviewSchedulingDialog({
  open,
  onOpenChange,
  applicationId,
  applicationName,
  onSuccess,
}: InterviewSchedulingDialogProps) {
  const [loading, setLoading] = useState(false)
  const [interviewType, setInterviewType] = useState('phone')
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledTime, setScheduledTime] = useState('')
  const [durationMinutes, setDurationMinutes] = useState('60')
  const [location, setLocation] = useState('')
  const [selectedInterviewers, setSelectedInterviewers] = useState<string[]>([])
  const { employees, loading: employeesLoading } = useEmployees()

  useEffect(() => {
    if (!open) {
      // Reset form when dialog closes
      setInterviewType('phone')
      setScheduledDate('')
      setScheduledTime('')
      setDurationMinutes('60')
      setLocation('')
      setSelectedInterviewers([])
    }
  }, [open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!scheduledDate || !scheduledTime) {
      alert('Please select both date and time for the interview')
      return
    }

    setLoading(true)
    try {
      // Combine date and time into a datetime string
      const scheduledDateTime = `${scheduledDate}T${scheduledTime}:00`
      const scheduledDateObj = new Date(scheduledDateTime)

      const interviewData: any = {
        application_id: applicationId,
        interview_type: interviewType,
        scheduled_date: scheduledDate, // Backend expects date only (YYYY-MM-DD)
        duration_minutes: durationMinutes ? parseInt(durationMinutes) : undefined,
        location: location || undefined,
        interviewer_ids: selectedInterviewers, // Array of UUID strings
      }

      // Remove undefined fields
      Object.keys(interviewData).forEach(key => {
        if (interviewData[key] === undefined) {
          delete interviewData[key]
        }
      })

      console.log('Scheduling interview with data:', interviewData)
      
      // Backend expects interviewer_ids in the request body
      const response = await api.post('/recruitment/interviews', interviewData)
      alert('Interview scheduled successfully!')
      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      console.error('Error scheduling interview:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Failed to schedule interview: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const toggleInterviewer = (employeeId: string) => {
    setSelectedInterviewers(prev =>
      prev.includes(employeeId)
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Schedule Interview</DialogTitle>
          <DialogDescription>
            Schedule an interview for {applicationName}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Interview Type *</Label>
            <Select value={interviewType} onValueChange={setInterviewType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="phone">Phone</SelectItem>
                <SelectItem value="video">Video</SelectItem>
                <SelectItem value="in-person">In-Person</SelectItem>
                <SelectItem value="panel">Panel</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Date *</Label>
              <Input
                type="date"
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                required
              />
            </div>
            <div>
              <Label>Time *</Label>
              <Input
                type="time"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <Label>Duration (minutes)</Label>
            <Input
              type="number"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(e.target.value)}
              placeholder="60"
              min="15"
              step="15"
            />
          </div>

          <div>
            <Label>Location</Label>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder={
                interviewType === 'phone'
                  ? 'Phone number or call link'
                  : interviewType === 'video'
                  ? 'Video call link (Zoom, Teams, etc.)'
                  : 'Physical address or meeting room'
              }
            />
          </div>

          <div>
            <Label>Interviewers</Label>
            {employeesLoading ? (
              <div className="text-sm text-gray-500">Loading employees...</div>
            ) : (
              <div className="mt-2 space-y-2 max-h-40 overflow-y-auto border rounded p-2">
                {employees.length === 0 ? (
                  <div className="text-sm text-gray-500">No employees available</div>
                ) : (
                  employees.map((employee) => (
                    <label
                      key={employee.id}
                      className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedInterviewers.includes(employee.id)}
                        onChange={() => toggleInterviewer(employee.id)}
                        className="rounded"
                      />
                      <span className="text-sm">
                        {employee.first_name} {employee.last_name}
                        {employee.position && ` - ${employee.position}`}
                      </span>
                    </label>
                  ))
                )}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Scheduling...' : 'Schedule Interview'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

