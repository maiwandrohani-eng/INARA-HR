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
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Target } from 'lucide-react'

interface SuccessionPlanFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  keyPositionId?: string
  onSubmitSuccess?: () => void
}

export function SuccessionPlanForm({ open, onOpenChange, keyPositionId, onSubmitSuccess }: SuccessionPlanFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [keyPositionIdValue, setKeyPositionIdValue] = useState(keyPositionId || '')
  const [planName, setPlanName] = useState('')
  const [planDate, setPlanDate] = useState(new Date().toISOString().split('T')[0])
  const [reviewDate, setReviewDate] = useState('')
  const [expectedTransitionDate, setExpectedTransitionDate] = useState('')
  const [riskMitigationStrategies, setRiskMitigationStrategies] = useState('')
  const [status, setStatus] = useState('draft')
  const [approvedById, setApprovedById] = useState('')
  const [approvedDate, setApprovedDate] = useState('')

  const resetForm = () => {
    setKeyPositionIdValue(keyPositionId || '')
    setPlanName('')
    setPlanDate(new Date().toISOString().split('T')[0])
    setReviewDate('')
    setExpectedTransitionDate('')
    setRiskMitigationStrategies('')
    setStatus('draft')
    setApprovedById('')
    setApprovedDate('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const planData = {
        key_position_id: keyPositionIdValue,
        plan_name: planName,
        plan_date: planDate,
        review_date: reviewDate || null,
        expected_transition_date: expectedTransitionDate || null,
        risk_mitigation_strategies: riskMitigationStrategies || null,
        status,
        approved_by: approvedById || null,
        approved_date: approvedDate || null,
      }

      await apiClient.post('/succession/succession-plans', planData)

      toast({
        title: 'Success',
        description: 'Succession plan created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating succession plan:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create succession plan',
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
            <Target className="h-6 w-6" />
            Create Succession Plan
          </DialogTitle>
          <DialogDescription>
            Develop a succession plan for a key position
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="key-position-id">Key Position ID *</Label>
            <Input
              id="key-position-id"
              value={keyPositionIdValue}
              onChange={(e) => setKeyPositionIdValue(e.target.value)}
              placeholder="Key Position UUID"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="plan-name">Plan Name *</Label>
            <Input
              id="plan-name"
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              placeholder="e.g., CEO Succession Plan 2025"
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="plan-date">Plan Date *</Label>
              <Input
                id="plan-date"
                type="date"
                value={planDate}
                onChange={(e) => setPlanDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="review-date">Review Date</Label>
              <Input
                id="review-date"
                type="date"
                value={reviewDate}
                onChange={(e) => setReviewDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="archived">Archived</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="expected-transition-date">Expected Transition Date</Label>
            <Input
              id="expected-transition-date"
              type="date"
              value={expectedTransitionDate}
              onChange={(e) => setExpectedTransitionDate(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="risk-mitigation">Risk Mitigation Strategies</Label>
            <Textarea
              id="risk-mitigation"
              value={riskMitigationStrategies}
              onChange={(e) => setRiskMitigationStrategies(e.target.value)}
              placeholder="Describe risk mitigation strategies for this succession plan"
              rows={4}
            />
          </div>

          {status === 'active' && (
            <div className="grid grid-cols-2 gap-4 border-t pt-4">
              <div className="space-y-2">
                <Label htmlFor="approved-by">Approved By</Label>
                <Input
                  id="approved-by"
                  value={approvedById}
                  onChange={(e) => setApprovedById(e.target.value)}
                  placeholder="Approver Employee UUID (optional)"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="approved-date">Approval Date</Label>
                <Input
                  id="approved-date"
                  type="date"
                  value={approvedDate}
                  onChange={(e) => setApprovedDate(e.target.value)}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Plan'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

