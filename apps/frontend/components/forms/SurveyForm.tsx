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
import { ClipboardList } from 'lucide-react'

interface SurveyFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function SurveyForm({ open, onOpenChange, onSubmitSuccess }: SurveyFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState('')
  const [surveyType, setSurveyType] = useState('')
  const [description, setDescription] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(true)
  const [targetAudience, setTargetAudience] = useState('all')

  const resetForm = () => {
    setTitle('')
    setSurveyType('')
    setDescription('')
    setStartDate('')
    setEndDate('')
    setIsAnonymous(true)
    setTargetAudience('all')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const surveyData = {
        title,
        survey_type: surveyType,
        description: description || null,
        start_date: startDate,
        end_date: endDate,
        is_anonymous: isAnonymous,
        is_active: true,
        target_audience: targetAudience,
      }

      await apiClient.post('/engagement/surveys', surveyData)

      toast({
        title: 'Success',
        description: 'Survey created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating survey:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create survey',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <ClipboardList className="h-6 w-6" />
            Create Survey
          </DialogTitle>
          <DialogDescription>
            Create a new employee engagement survey
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">Survey Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Q1 2025 Employee Engagement Survey"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="survey-type">Survey Type *</Label>
              <Select value={surveyType} onValueChange={setSurveyType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pulse">Pulse Survey</SelectItem>
                  <SelectItem value="annual">Annual Survey</SelectItem>
                  <SelectItem value="onboarding">Onboarding</SelectItem>
                  <SelectItem value="exit">Exit Survey</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
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
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Survey description and instructions"
              rows={4}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Start Date *</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end-date">End Date *</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="is-anonymous"
              checked={isAnonymous}
              onCheckedChange={setIsAnonymous}
            />
            <Label htmlFor="is-anonymous">Anonymous Responses</Label>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Survey'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

