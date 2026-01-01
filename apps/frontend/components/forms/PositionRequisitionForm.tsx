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
import { Target } from 'lucide-react'

interface PositionRequisitionFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function PositionRequisitionForm({ open, onOpenChange, onSubmitSuccess }: PositionRequisitionFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [jobTitle, setJobTitle] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [justification, setJustification] = useState('')
  const [businessCase, setBusinessCase] = useState('')
  const [salaryMin, setSalaryMin] = useState('')
  const [salaryMax, setSalaryMax] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [requestedStartDate, setRequestedStartDate] = useState('')
  const [urgency, setUrgency] = useState('normal')

  useEffect(() => {
    // Fetch current user to get employee_id
    const fetchUser = async () => {
      try {
        const response = await apiClient.get('/auth/me')
        setCurrentUser(response.data)
      } catch (error) {
        console.error('Failed to fetch current user:', error)
      }
    }
    if (open) {
      fetchUser()
    }
  }, [open])

  const resetForm = () => {
    setJobTitle('')
    setEmploymentType('')
    setDepartmentId('')
    setJustification('')
    setBusinessCase('')
    setSalaryMin('')
    setSalaryMax('')
    setCurrency('USD')
    setRequestedStartDate('')
    setUrgency('normal')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const requisitionData = {
        department_id: departmentId,
        job_title: jobTitle,
        employment_type: employmentType,
        justification,
        business_case: businessCase || null,
        budgeted_salary_min: salaryMin ? parseFloat(salaryMin) : null,
        budgeted_salary_max: salaryMax ? parseFloat(salaryMax) : null,
        currency,
        requested_start_date: requestedStartDate || null,
        urgency,
        status: 'draft',
        requested_by: currentUser?.employee_id || null, // Backend will handle this if null
      }

      await apiClient.post('/workforce/requisitions', requisitionData)

      toast({
        title: 'Success',
        description: 'Position requisition created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating requisition:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create requisition',
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
            <Target className="h-6 w-6" />
            New Position Requisition
          </DialogTitle>
          <DialogDescription>
            Request approval for a new position
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="job-title">Job Title *</Label>
              <Input
                id="job-title"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g., Senior Software Engineer"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="employment-type">Employment Type *</Label>
              <Select value={employmentType} onValueChange={setEmploymentType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full_time">Full Time</SelectItem>
                  <SelectItem value="part_time">Part Time</SelectItem>
                  <SelectItem value="contract">Contract</SelectItem>
                  <SelectItem value="temporary">Temporary</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="department-id">Department ID *</Label>
              <Input
                id="department-id"
                value={departmentId}
                onChange={(e) => setDepartmentId(e.target.value)}
                placeholder="Department UUID"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="urgency">Urgency</Label>
              <Select value={urgency} onValueChange={setUrgency}>
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
          </div>

          <div className="space-y-2">
            <Label htmlFor="justification">Justification *</Label>
            <Textarea
              id="justification"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Explain why this position is needed"
              rows={4}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="business-case">Business Case</Label>
            <Textarea
              id="business-case"
              value={businessCase}
              onChange={(e) => setBusinessCase(e.target.value)}
              placeholder="Business case and strategic rationale"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salary-min">Budgeted Salary Min</Label>
              <Input
                id="salary-min"
                type="number"
                step="0.01"
                value={salaryMin}
                onChange={(e) => setSalaryMin(e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="salary-max">Budgeted Salary Max</Label>
              <Input
                id="salary-max"
                type="number"
                step="0.01"
                value={salaryMax}
                onChange={(e) => setSalaryMax(e.target.value)}
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
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="requested-start-date">Requested Start Date</Label>
            <Input
              id="requested-start-date"
              type="date"
              value={requestedStartDate}
              onChange={(e) => setRequestedStartDate(e.target.value)}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Requisition'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

