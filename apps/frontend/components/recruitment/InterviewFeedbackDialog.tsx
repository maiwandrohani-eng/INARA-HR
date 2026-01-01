'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api-client'

interface InterviewFeedbackDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  interviewId: string
  onSuccess?: () => void
}

export function InterviewFeedbackDialog({
  open,
  onOpenChange,
  interviewId,
  onSuccess,
}: InterviewFeedbackDialogProps) {
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [rating, setRating] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!feedback.trim()) {
      alert('Please provide interview feedback')
      return
    }

    setLoading(true)
    try {
      const feedbackData = {
        feedback: feedback,
        rating: rating ? parseInt(rating) : undefined,
      }

      await api.post(`/recruitment/interviews/${interviewId}/feedback`, feedbackData)
      alert('Interview feedback submitted successfully!')
      onOpenChange(false)
      setFeedback('')
      setRating('')
      onSuccess?.()
    } catch (error: any) {
      console.error('Error submitting feedback:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Failed to submit feedback: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Submit Interview Feedback</DialogTitle>
          <DialogDescription>
            Provide feedback and rating for this interview
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Rating (1-5)</Label>
            <Select value={rating} onValueChange={setRating}>
              <SelectTrigger>
                <SelectValue placeholder="Select rating (optional)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 - Poor</SelectItem>
                <SelectItem value="2">2 - Fair</SelectItem>
                <SelectItem value="3">3 - Good</SelectItem>
                <SelectItem value="4">4 - Very Good</SelectItem>
                <SelectItem value="5">5 - Excellent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Feedback *</Label>
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Provide detailed feedback about the candidate's performance, skills, communication, fit for the role, etc."
              rows={8}
              required
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

