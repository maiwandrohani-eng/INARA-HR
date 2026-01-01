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
import { useEmployees } from '@/hooks/useEmployees'
import { useAuthStore } from '@/state/auth.store'
import { Award } from 'lucide-react'

interface RecognitionFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function RecognitionForm({ open, onOpenChange, onSubmitSuccess }: RecognitionFormProps) {
  const { toast } = useToast()
  const { employees } = useEmployees()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [employeeId, setEmployeeId] = useState('')
  const [recognitionType, setRecognitionType] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [recognitionDate, setRecognitionDate] = useState(new Date().toISOString().split('T')[0])
  const [isPublic, setIsPublic] = useState(true)

  const resetForm = () => {
    setEmployeeId('')
    setRecognitionType('')
    setTitle('')
    setDescription('')
    setRecognitionDate(new Date().toISOString().split('T')[0])
    setIsPublic(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Get recognized_by_id from current user's employee record
      // For now, using a placeholder - in production, fetch from user.employee_id
      const recognitionData = {
        employee_id: employeeId,
        recognized_by_id: user?.employee_id || '00000000-0000-0000-0000-000000000000', // Placeholder
        recognition_type: recognitionType,
        title,
        description,
        recognition_date: recognitionDate,
        is_public: isPublic,
      }

      await apiClient.post('/engagement/recognitions', recognitionData)

      toast({
        title: 'Success',
        description: 'Recognition created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating recognition:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create recognition',
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
            <Award className="h-6 w-6" />
            Recognize Employee
          </DialogTitle>
          <DialogDescription>
            Create a recognition or award for an employee
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="employee">Employee *</Label>
              <Select value={employeeId} onValueChange={setEmployeeId} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select employee" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id}>
                      {emp.full_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="recognition-type">Recognition Type *</Label>
              <Select value={recognitionType} onValueChange={setRecognitionType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="achievement">Achievement</SelectItem>
                  <SelectItem value="milestone">Milestone</SelectItem>
                  <SelectItem value="excellence">Excellence</SelectItem>
                  <SelectItem value="peer_recognition">Peer Recognition</SelectItem>
                  <SelectItem value="anniversary">Work Anniversary</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Outstanding Performance, 5 Year Milestone"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe why this employee is being recognized"
              rows={5}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="recognition-date">Recognition Date *</Label>
              <Input
                id="recognition-date"
                type="date"
                value={recognitionDate}
                onChange={(e) => setRecognitionDate(e.target.value)}
                required
              />
            </div>

            <div className="flex items-center space-x-2 pt-8">
              <Switch
                id="is-public"
                checked={isPublic}
                onCheckedChange={setIsPublic}
              />
              <Label htmlFor="is-public">Make Public</Label>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Recognition'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

