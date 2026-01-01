'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api-client'

interface OfferLetterDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  applicationId: string
  applicationName: string
  jobTitle?: string
  onSuccess?: () => void
}

export function OfferLetterDialog({
  open,
  onOpenChange,
  applicationId,
  applicationName,
  jobTitle,
  onSuccess,
}: OfferLetterDialogProps) {
  const [loading, setLoading] = useState(false)
  const [positionTitle, setPositionTitle] = useState(jobTitle || '')
  const [salary, setSalary] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [startDate, setStartDate] = useState('')
  const [expiryDate, setExpiryDate] = useState('')

  useEffect(() => {
    if (!open) {
      // Reset form when dialog closes
      setPositionTitle(jobTitle || '')
      setSalary('')
      setCurrency('USD')
      setStartDate('')
      setExpiryDate('')
    } else if (jobTitle) {
      setPositionTitle(jobTitle)
    }
  }, [open, jobTitle])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!positionTitle || !salary || !startDate) {
      alert('Please fill in all required fields (Position, Salary, Start Date)')
      return
    }

    setLoading(true)
    try {
      const offerData = {
        application_id: applicationId,
        position_title: positionTitle,
        salary: salary,
        currency: currency,
        start_date: startDate,
      }

      console.log('Creating offer letter with data:', offerData)
      const response = await api.post('/recruitment/offers', offerData)
      console.log('Offer letter created:', response)

      // Optionally send the offer immediately
      const sendOffer = confirm('Offer letter created successfully! Would you like to send it to the candidate now?')
      
      if (sendOffer && response.id) {
        try {
          await api.post(`/recruitment/offers/${response.id}/send`)
          alert('Offer letter sent to candidate!')
        } catch (sendError: any) {
          console.error('Error sending offer:', sendError)
          alert(`Offer created but failed to send: ${sendError.response?.data?.detail || sendError.message}`)
        }
      }

      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      console.error('Error creating offer letter:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
      alert(`Failed to create offer letter: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Offer Letter</DialogTitle>
          <DialogDescription>
            Create an offer letter for {applicationName}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Position Title *</Label>
            <Input
              value={positionTitle}
              onChange={(e) => setPositionTitle(e.target.value)}
              placeholder="e.g., Senior Software Engineer"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Salary *</Label>
              <Input
                value={salary}
                onChange={(e) => setSalary(e.target.value)}
                placeholder="e.g., 75000 or 75,000"
                required
              />
            </div>
            <div>
              <Label>Currency</Label>
              <Input
                value={currency}
                onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                placeholder="USD"
                maxLength={3}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Start Date *</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div>
              <Label>Offer Expiry Date (Optional)</Label>
              <Input
                type="date"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Offer Letter'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

