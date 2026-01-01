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
import { UserCheck } from 'lucide-react'

interface KeyPositionFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function KeyPositionForm({ open, onOpenChange, onSubmitSuccess }: KeyPositionFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [positionId, setPositionId] = useState('')
  const [criticalityLevel, setCriticalityLevel] = useState('')
  const [businessImpact, setBusinessImpact] = useState('')
  const [vacancyRisk, setVacancyRisk] = useState('')
  const [currentIncumbentId, setCurrentIncumbentId] = useState('')

  const resetForm = () => {
    setPositionId('')
    setCriticalityLevel('')
    setBusinessImpact('')
    setVacancyRisk('')
    setCurrentIncumbentId('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const positionData = {
        position_id: positionId,
        criticality_level: criticalityLevel,
        business_impact: businessImpact || null,
        vacancy_risk: vacancyRisk || null,
        current_incumbent_id: currentIncumbentId || null,
        has_successor: false,
        succession_status: 'not_planned',
      }

      await apiClient.post('/succession/key-positions', positionData)

      toast({
        title: 'Success',
        description: 'Key position created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating key position:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create key position',
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
            <UserCheck className="h-6 w-6" />
            Add Key Position
          </DialogTitle>
          <DialogDescription>
            Identify a critical position for succession planning
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="position-id">Position ID *</Label>
            <Input
              id="position-id"
              value={positionId}
              onChange={(e) => setPositionId(e.target.value)}
              placeholder="Position UUID"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="criticality">Criticality Level *</Label>
              <Select value={criticalityLevel} onValueChange={setCriticalityLevel} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="vacancy-risk">Vacancy Risk</Label>
              <Select value={vacancyRisk} onValueChange={setVacancyRisk}>
                <SelectTrigger>
                  <SelectValue placeholder="Select risk" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="current-incumbent">Current Incumbent ID</Label>
            <Input
              id="current-incumbent"
              value={currentIncumbentId}
              onChange={(e) => setCurrentIncumbentId(e.target.value)}
              placeholder="Employee UUID (optional)"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="business-impact">Business Impact</Label>
            <Textarea
              id="business-impact"
              value={businessImpact}
              onChange={(e) => setBusinessImpact(e.target.value)}
              placeholder="Describe the business impact if this position becomes vacant"
              rows={4}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Add Key Position'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

