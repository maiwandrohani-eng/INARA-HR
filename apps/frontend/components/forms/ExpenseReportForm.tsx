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
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Receipt } from 'lucide-react'
import { useAuthStore } from '@/state/auth.store'

interface ExpenseReportFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function ExpenseReportForm({ open, onOpenChange, onSubmitSuccess }: ExpenseReportFormProps) {
  const { toast } = useToast()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0])
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')
  const [description, setDescription] = useState('')

  const resetForm = () => {
    setReportDate(new Date().toISOString().split('T')[0])
    setPeriodStart('')
    setPeriodEnd('')
    setDescription('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // For now, we'll need to get the employee_id from the user
      // This is a simplified version - in production, you'd get this from the employee record
      const reportData = {
        employee_id: user?.employee_id || '00000000-0000-0000-0000-000000000000', // Placeholder
        report_date: reportDate,
        period_start: periodStart || null,
        period_end: periodEnd || null,
        total_amount: 0, // Will be calculated from items
        description: description || null,
        status: 'draft',
      }

      await apiClient.post('/expenses/reports', reportData)

      toast({
        title: 'Success',
        description: 'Expense report created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating expense report:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create expense report',
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
            <Receipt className="h-6 w-6" />
            New Expense Report
          </DialogTitle>
          <DialogDescription>
            Create a new expense report
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="report-date">Report Date *</Label>
            <Input
              id="report-date"
              type="date"
              value={reportDate}
              onChange={(e) => setReportDate(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="period-start">Period Start</Label>
              <Input
                id="period-start"
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="period-end">Period End</Label>
              <Input
                id="period-end"
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Report description or notes"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Report'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

