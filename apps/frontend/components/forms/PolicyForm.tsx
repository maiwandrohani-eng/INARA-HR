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
import { Scale } from 'lucide-react'

interface PolicyFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function PolicyForm({ open, onOpenChange, onSubmitSuccess }: PolicyFormProps) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState('')
  const [policyType, setPolicyType] = useState('')
  const [version, setVersion] = useState('1.0')
  const [content, setContent] = useState('')
  const [documentUrl, setDocumentUrl] = useState('')
  const [effectiveDate, setEffectiveDate] = useState('')
  const [expiryDate, setExpiryDate] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [requiresAcknowledgment, setRequiresAcknowledgment] = useState(true)
  const [applicableTo, setApplicableTo] = useState('all')

  const resetForm = () => {
    setTitle('')
    setPolicyType('')
    setVersion('1.0')
    setContent('')
    setDocumentUrl('')
    setEffectiveDate('')
    setExpiryDate('')
    setIsActive(true)
    setRequiresAcknowledgment(true)
    setApplicableTo('all')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const policyData = {
        title,
        policy_type: policyType,
        version,
        content: content || null,
        document_url: documentUrl || null,
        effective_date: effectiveDate,
        expiry_date: expiryDate || null,
        is_active: isActive,
        requires_acknowledgment: requiresAcknowledgment,
        applicable_to: applicableTo,
      }

      await apiClient.post('/compliance/policies', policyData)

      toast({
        title: 'Success',
        description: 'Policy created successfully',
      })

      resetForm()
      onOpenChange(false)
      onSubmitSuccess?.()
    } catch (error: any) {
      console.error('Error creating policy:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create policy',
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
            <Scale className="h-6 w-6" />
            Add Policy
          </DialogTitle>
          <DialogDescription>
            Create a new company policy requiring employee acknowledgment
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">Policy Title *</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Code of Conduct, Data Protection Policy"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="policy-type">Policy Type *</Label>
              <Select value={policyType} onValueChange={setPolicyType} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hr_policy">HR Policy</SelectItem>
                  <SelectItem value="code_of_conduct">Code of Conduct</SelectItem>
                  <SelectItem value="safety">Safety</SelectItem>
                  <SelectItem value="data_protection">Data Protection</SelectItem>
                  <SelectItem value="it_policy">IT Policy</SelectItem>
                  <SelectItem value="travel_policy">Travel Policy</SelectItem>
                  <SelectItem value="anti_harassment">Anti-Harassment</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="version">Version *</Label>
              <Input
                id="version"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="e.g., 1.0, 2.1"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="applicable-to">Applicable To</Label>
              <Select value={applicableTo} onValueChange={setApplicableTo}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Employees</SelectItem>
                  <SelectItem value="department">Specific Department</SelectItem>
                  <SelectItem value="role">Specific Role</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="effective-date">Effective Date *</Label>
              <Input
                id="effective-date"
                type="date"
                value={effectiveDate}
                onChange={(e) => setEffectiveDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="expiry-date">Expiry Date</Label>
              <Input
                id="expiry-date"
                type="date"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="content">Policy Content</Label>
            <Textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Policy content and details"
              rows={6}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="document-url">Document URL</Label>
            <Input
              id="document-url"
              value={documentUrl}
              onChange={(e) => setDocumentUrl(e.target.value)}
              placeholder="URL to policy document (optional)"
            />
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Switch
                id="is-active"
                checked={isActive}
                onCheckedChange={setIsActive}
              />
              <Label htmlFor="is-active">Active</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="requires-acknowledgment"
                checked={requiresAcknowledgment}
                onCheckedChange={setRequiresAcknowledgment}
              />
              <Label htmlFor="requires-acknowledgment">Requires Acknowledgment</Label>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Policy'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

