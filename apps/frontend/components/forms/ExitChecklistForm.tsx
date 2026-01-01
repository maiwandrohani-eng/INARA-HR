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
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'
import { ListChecks } from 'lucide-react'

interface ExitChecklistFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function ExitChecklistForm({ open, onOpenChange, onSubmitSuccess }: ExitChecklistFormProps) {
  const { toast } = useToast()
  const { employees } = useEmployees()
  const [loading, setLoading] = useState(false)
  const [resignationId, setResignationId] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [checklistItem, setChecklistItem] = useState('')
  const [category, setCategory] = useState('')
  const [assignedTo, setAssignedTo] = useState('')
  const [isCritical, setIsCritical] = useState(false)
  const [dueDate, setDueDate] = useState('')
  const [verificationRequired, setVerificationRequired] = useState(false)
  const [notes, setNotes] = useState('')

  const resetForm = () => {
    setResignationId('')
    setEmployeeId('')
    setChecklistItem('')
    setCategory('')
    setAssignedTo('')
    setIsCritical(false)
    setDueDate('')
    setVerificationRequired(false)
    setNotes('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const checklistData = {
        resignation_id: resignationId,
        employee_id: employeeId,
        checklist_item: checklistItem,
        category,
        assigned_to: assignedTo || null,
        is_critical: isCritical,
        due_date: dueDate || null,
        verification_required: verificationRequired,
        notes: notes || null,
        is_completed: false,
      }

      await apiClient.post('/exit/exit-checklists', checklistData)

      toast({
        title: 'Success',
        description: 'Exit checklist item created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating exit checklist:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create checklist item',
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
            <ListChecks className="h-6 w-6" />
            Add Exit Checklist Item
          </DialogTitle>
          <DialogDescription>
            Add an item to the exit process checklist
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
              <Label htmlFor="employee">Employee *</Label>
              <Select value={employeeId} onValueChange={setEmployeeId} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select employee" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id}>
                      {getEmployeeFullName(emp)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="checklist-item">Checklist Item *</Label>
            <Input
              id="checklist-item"
              value={checklistItem}
              onChange={(e) => setChecklistItem(e.target.value)}
              placeholder="e.g., Return laptop, Clear access, Handover documents"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select value={category} onValueChange={setCategory} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="it">IT</SelectItem>
                  <SelectItem value="hr">HR</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="security">Security</SelectItem>
                  <SelectItem value="knowledge_transfer">Knowledge Transfer</SelectItem>
                  <SelectItem value="access">Access Control</SelectItem>
                  <SelectItem value="equipment">Equipment Return</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="assigned-to">Assigned To</Label>
              <Select value={assignedTo} onValueChange={setAssignedTo}>
                <SelectTrigger>
                  <SelectValue placeholder="Select assignee" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Unassigned</SelectItem>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={emp.id}>
                      {getEmployeeFullName(emp)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="due-date">Due Date</Label>
            <Input
              id="due-date"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes or instructions"
              rows={3}
            />
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is-critical"
                checked={isCritical}
                onChange={(e) => setIsCritical(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <Label htmlFor="is-critical">Critical Item</Label>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="verification-required"
                checked={verificationRequired}
                onChange={(e) => setVerificationRequired(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <Label htmlFor="verification-required">Verification Required</Label>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Add Item'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

