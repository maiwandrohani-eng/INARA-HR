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
import { useEmployees } from '@/hooks/useEmployees'
import { BookOpen } from 'lucide-react'

interface KnowledgeTransferFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function KnowledgeTransferForm({ open, onOpenChange, onSubmitSuccess }: KnowledgeTransferFormProps) {
  const { toast } = useToast()
  const { employees } = useEmployees()
  const [loading, setLoading] = useState(false)
  const [resignationId, setResignationId] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [transferredToId, setTransferredToId] = useState('')
  const [knowledgeArea, setKnowledgeArea] = useState('')
  const [description, setDescription] = useState('')
  const [transferDate, setTransferDate] = useState('')
  const [documentUrl, setDocumentUrl] = useState('')
  const [resources, setResources] = useState('')

  const resetForm = () => {
    setResignationId('')
    setEmployeeId('')
    setTransferredToId('')
    setKnowledgeArea('')
    setDescription('')
    setTransferDate('')
    setDocumentUrl('')
    setResources('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const transferData = {
        resignation_id: resignationId,
        employee_id: employeeId,
        transferred_to_id: transferredToId || null,
        knowledge_area: knowledgeArea,
        description,
        transfer_date: transferDate || null,
        document_url: documentUrl || null,
        resources: resources || null,
        is_complete: false,
      }

      await apiClient.post('/exit/knowledge-transfers', transferData)

      toast({
        title: 'Success',
        description: 'Knowledge transfer recorded successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating knowledge transfer:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to record knowledge transfer',
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
            <BookOpen className="h-6 w-6" />
            Document Knowledge Transfer
          </DialogTitle>
          <DialogDescription>
            Record knowledge and information being transferred
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
              <Label htmlFor="transfer-date">Transfer Date</Label>
              <Input
                id="transfer-date"
                type="date"
                value={transferDate}
                onChange={(e) => setTransferDate(e.target.value)}
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
              <Label htmlFor="transferred-to">Transferred To</Label>
              <Select value={transferredToId} onValueChange={setTransferredToId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select recipient" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Not yet transferred</SelectItem>
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
            <Label htmlFor="knowledge-area">Knowledge Area *</Label>
            <Input
              id="knowledge-area"
              value={knowledgeArea}
              onChange={(e) => setKnowledgeArea(e.target.value)}
              placeholder="e.g., Project ABC, Client XYZ, System Admin, Process Documentation"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detailed description of knowledge being transferred"
              rows={5}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="document-url">Document URL</Label>
            <Input
              id="document-url"
              value={documentUrl}
              onChange={(e) => setDocumentUrl(e.target.value)}
              placeholder="URL to documentation or resources"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="resources">Resources</Label>
            <Textarea
              id="resources"
              value={resources}
              onChange={(e) => setResources(e.target.value)}
              placeholder="List of resources, files, or links (JSON format or comma-separated)"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Record Transfer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

