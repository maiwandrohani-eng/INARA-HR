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
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { useEmployees } from '@/hooks/useEmployees'
import { DoorOpen } from 'lucide-react'

interface ExitInterviewFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function ExitInterviewForm({ open, onOpenChange, onSubmitSuccess }: ExitInterviewFormProps) {
  const { toast } = useToast()
  const { employees, loading: employeesLoading } = useEmployees()
  const [loading, setLoading] = useState(false)
  const [resignationId, setResignationId] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [conductedById, setConductedById] = useState('')
  const [interviewDate, setInterviewDate] = useState(new Date().toISOString().split('T')[0])
  const [interviewType, setInterviewType] = useState('face_to_face')
  const [q1Reason, setQ1Reason] = useState('')
  const [q2Satisfaction, setQ2Satisfaction] = useState('')
  const [q3Management, setQ3Management] = useState('')
  const [q4Environment, setQ4Environment] = useState('')
  const [q5Recommend, setQ5Recommend] = useState('')
  const [q6Suggestions, setQ6Suggestions] = useState('')
  const [q7Positive, setQ7Positive] = useState('')
  const [q8Plans, setQ8Plans] = useState('')
  const [overallFeedback, setOverallFeedback] = useState('')

  const resetForm = () => {
    setResignationId('')
    setEmployeeId('')
    setConductedById('')
    setInterviewDate(new Date().toISOString().split('T')[0])
    setInterviewType('face_to_face')
    setQ1Reason('')
    setQ2Satisfaction('')
    setQ3Management('')
    setQ4Environment('')
    setQ5Recommend('')
    setQ6Suggestions('')
    setQ7Positive('')
    setQ8Plans('')
    setOverallFeedback('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const interviewData = {
        resignation_id: resignationId,
        employee_id: employeeId,
        conducted_by_id: conductedById,
        interview_date: interviewDate,
        interview_type: interviewType,
        q1_reason_for_leaving: q1Reason || null,
        q2_overall_satisfaction: q2Satisfaction ? parseInt(q2Satisfaction) : null,
        q3_management_rating: q3Management ? parseInt(q3Management) : null,
        q4_work_environment_rating: q4Environment ? parseInt(q4Environment) : null,
        q5_would_recommend: q5Recommend ? q5Recommend === 'yes' : null,
        q6_improvement_suggestions: q6Suggestions || null,
        q7_positive_feedback: q7Positive || null,
        q8_future_plans: q8Plans || null,
        overall_feedback: overallFeedback || null,
        is_complete: true,
      }

      await apiClient.post('/exit/exit-interviews', interviewData)

      toast({
        title: 'Success',
        description: 'Exit interview recorded successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating exit interview:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to record exit interview',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <DoorOpen className="h-6 w-6" />
            Conduct Exit Interview
          </DialogTitle>
          <DialogDescription>
            Record exit interview responses from departing employee
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="resignation-id">Resignation ID *</Label>
              <Input
                id="resignation-id"
                value={resignationId}
                onChange={(e) => setResignationId(e.target.value)}
                placeholder="Resignation ID"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="interview-date">Interview Date *</Label>
              <Input
                id="interview-date"
                type="date"
                value={interviewDate}
                onChange={(e) => setInterviewDate(e.target.value)}
                required
              />
            </div>
          </div>

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
              <Label htmlFor="conducted-by">Conducted By *</Label>
              <Select value={conductedById} onValueChange={setConductedById} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select interviewer" />
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
          </div>

          <div className="space-y-2">
            <Label htmlFor="interview-type">Interview Type</Label>
            <Select value={interviewType} onValueChange={setInterviewType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="face_to_face">Face to Face</SelectItem>
                <SelectItem value="phone">Phone</SelectItem>
                <SelectItem value="video">Video Call</SelectItem>
                <SelectItem value="online_survey">Online Survey</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-4 border-t pt-4">
            <h3 className="text-lg font-semibold">Interview Questions</h3>

            <div className="space-y-2">
              <Label htmlFor="q1">1. What is your main reason for leaving? *</Label>
              <Textarea
                id="q1"
                value={q1Reason}
                onChange={(e) => setQ1Reason(e.target.value)}
                placeholder="Please provide your reason for leaving"
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="q2">2. Overall Satisfaction (1-10)</Label>
                <Input
                  id="q2"
                  type="number"
                  min="1"
                  max="10"
                  value={q2Satisfaction}
                  onChange={(e) => setQ2Satisfaction(e.target.value)}
                  placeholder="1-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="q3">3. Management Rating (1-10)</Label>
                <Input
                  id="q3"
                  type="number"
                  min="1"
                  max="10"
                  value={q3Management}
                  onChange={(e) => setQ3Management(e.target.value)}
                  placeholder="1-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="q4">4. Work Environment (1-10)</Label>
                <Input
                  id="q4"
                  type="number"
                  min="1"
                  max="10"
                  value={q4Environment}
                  onChange={(e) => setQ4Environment(e.target.value)}
                  placeholder="1-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="q5">5. Would you recommend this company?</Label>
              <Select value={q5Recommend} onValueChange={setQ5Recommend}>
                <SelectTrigger>
                  <SelectValue placeholder="Select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="yes">Yes</SelectItem>
                  <SelectItem value="no">No</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="q6">6. What improvements would you suggest?</Label>
              <Textarea
                id="q6"
                value={q6Suggestions}
                onChange={(e) => setQ6Suggestions(e.target.value)}
                placeholder="Suggestions for improvement"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="q7">7. What did you enjoy most about working here?</Label>
              <Textarea
                id="q7"
                value={q7Positive}
                onChange={(e) => setQ7Positive(e.target.value)}
                placeholder="Positive feedback"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="q8">8. What are your future plans?</Label>
              <Textarea
                id="q8"
                value={q8Plans}
                onChange={(e) => setQ8Plans(e.target.value)}
                placeholder="Future plans"
                rows={2}
              />
            </div>
          </div>

          <div className="space-y-2 border-t pt-4">
            <Label htmlFor="overall">Overall Feedback/Summary</Label>
            <Textarea
              id="overall"
              value={overallFeedback}
              onChange={(e) => setOverallFeedback(e.target.value)}
              placeholder="Overall feedback and summary"
              rows={4}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Interview'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

