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
import { Heart } from 'lucide-react'

interface BenefitPlanFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function BenefitPlanForm({ open, onOpenChange, onSubmitSuccess }: BenefitPlanFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')
  const [benefitType, setBenefitType] = useState('')
  const [provider, setProvider] = useState('')
  const [description, setDescription] = useState('')
  const [coverageStartDate, setCoverageStartDate] = useState('')
  const [coverageEndDate, setCoverageEndDate] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [employerContributionAmount, setEmployerContributionAmount] = useState('')
  const [employeeCost, setEmployeeCost] = useState('')
  const [currency, setCurrency] = useState('USD')

  const resetForm = () => {
    setName('')
    setBenefitType('')
    setProvider('')
    setDescription('')
    setCoverageStartDate('')
    setCoverageEndDate('')
    setIsActive(true)
    setEmployerContributionAmount('')
    setEmployeeCost('')
    setCurrency('USD')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const planData = {
        name,
        benefit_type: benefitType,
        provider: provider || null,
        description: description || null,
        coverage_start_date: coverageStartDate || null,
        coverage_end_date: coverageEndDate || null,
        is_active: isActive,
        employer_contribution_amount: employerContributionAmount ? parseFloat(employerContributionAmount) : null,
        employee_cost_per_pay_period: employeeCost ? parseFloat(employeeCost) : null,
        currency,
      }

      await apiClient.post('/benefits/plans', planData)

      toast({
        title: 'Success',
        description: 'Benefit plan created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating benefit plan:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create benefit plan',
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
            <Heart className="h-6 w-6" />
            Add Benefit Plan
          </DialogTitle>
          <DialogDescription>
            Create a new benefit plan for employees
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Plan Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Health Insurance Premium"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="benefit-type">Benefit Type *</Label>
              <Select value={benefitType} onValueChange={setBenefitType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="health_insurance">Health Insurance</SelectItem>
                  <SelectItem value="dental">Dental</SelectItem>
                  <SelectItem value="vision">Vision</SelectItem>
                  <SelectItem value="life_insurance">Life Insurance</SelectItem>
                  <SelectItem value="retirement">Retirement</SelectItem>
                  <SelectItem value="fsa">FSA</SelectItem>
                  <SelectItem value="hsa">HSA</SelectItem>
                  <SelectItem value="disability">Disability</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="provider">Provider</Label>
            <Input
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              placeholder="Insurance provider name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Plan details and coverage information"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="coverage-start">Coverage Start Date</Label>
              <Input
                id="coverage-start"
                type="date"
                value={coverageStartDate}
                onChange={(e) => setCoverageStartDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="coverage-end">Coverage End Date</Label>
              <Input
                id="coverage-end"
                type="date"
                value={coverageEndDate}
                onChange={(e) => setCoverageEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="employer-contribution">Employer Contribution</Label>
              <Input
                id="employer-contribution"
                type="number"
                step="0.01"
                value={employerContributionAmount}
                onChange={(e) => setEmployerContributionAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="employee-cost">Employee Cost per Pay Period</Label>
              <Input
                id="employee-cost"
                type="number"
                step="0.01"
                value={employeeCost}
                onChange={(e) => setEmployeeCost(e.target.value)}
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

          <div className="flex items-center space-x-2">
            <Switch
              id="is-active"
              checked={isActive}
              onCheckedChange={setIsActive}
            />
            <Label htmlFor="is-active">Active</Label>
          </div>

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

