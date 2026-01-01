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
import { Calendar } from 'lucide-react'

interface WorkforcePlanFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function WorkforcePlanForm({ open, onOpenChange, onSubmitSuccess }: WorkforcePlanFormProps) {
  const { toast } = useToast()
  const { employees } = useEmployees()
  const [loading, setLoading] = useState(false)
  const [planName, setPlanName] = useState('')
  const [planYear, setPlanYear] = useState(new Date().getFullYear().toString())
  const [planStartDate, setPlanStartDate] = useState('')
  const [planEndDate, setPlanEndDate] = useState('')
  const [status, setStatus] = useState('draft')
  const [totalBudget, setTotalBudget] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [approvedById, setApprovedById] = useState('')
  const [approvedDate, setApprovedDate] = useState('')

  useEffect(() => {
    // Set default dates
    if (open && !planStartDate) {
      const year = parseInt(planYear) || new Date().getFullYear()
      setPlanStartDate(`${year}-01-01`)
      setPlanEndDate(`${year}-12-31`)
    }
  }, [open, planYear, planStartDate])

  const resetForm = () => {
    setPlanName('')
    setPlanYear(new Date().getFullYear().toString())
    setPlanStartDate('')
    setPlanEndDate('')
    setStatus('draft')
    setTotalBudget('')
    setCurrency('USD')
    setApprovedById('')
    setApprovedDate('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const planData = {
        plan_name: planName,
        plan_year: parseInt(planYear),
        plan_start_date: planStartDate,
        plan_end_date: planEndDate,
        status,
        total_budget: totalBudget ? parseFloat(totalBudget) : null,
        currency,
        approved_by: approvedById || null,
        approved_date: approvedDate || null,
      }

      await apiClient.post('/workforce/plans', planData)

      toast({
        title: 'Success',
        description: 'Workforce plan created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating workforce plan:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create workforce plan',
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
            <Calendar className="h-6 w-6" />
            Create Workforce Plan
          </DialogTitle>
          <DialogDescription>
            Create a strategic workforce plan for the organization
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="plan-name">Plan Name *</Label>
              <Input
                id="plan-name"
                value={planName}
                onChange={(e) => setPlanName(e.target.value)}
                placeholder="e.g., 2025 Annual Workforce Plan"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="plan-year">Plan Year *</Label>
              <Input
                id="plan-year"
                type="number"
                value={planYear}
                onChange={(e) => {
                  setPlanYear(e.target.value)
                  const year = parseInt(e.target.value) || new Date().getFullYear()
                  setPlanStartDate(`${year}-01-01`)
                  setPlanEndDate(`${year}-12-31`)
                }}
                required
                min="2020"
                max="2100"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="plan-start-date">Start Date *</Label>
              <Input
                id="plan-start-date"
                type="date"
                value={planStartDate}
                onChange={(e) => setPlanStartDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="plan-end-date">End Date *</Label>
              <Input
                id="plan-end-date"
                type="date"
                value={planEndDate}
                onChange={(e) => setPlanEndDate(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="archived">Archived</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="total-budget">Total Budget</Label>
              <Input
                id="total-budget"
                type="number"
                step="0.01"
                value={totalBudget}
                onChange={(e) => setTotalBudget(e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency</Label>
              <Select value={currency} onValueChange={setCurrency}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                  <SelectItem value="GBP">GBP</SelectItem>
                  <SelectItem value="AFN">AFN</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {status === 'approved' && (
            <div className="grid grid-cols-2 gap-4 border-t pt-4">
              <div className="space-y-2">
                <Label htmlFor="approved-by">Approved By</Label>
                <Select value={approvedById} onValueChange={setApprovedById}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select approver" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Not specified</SelectItem>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.full_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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

