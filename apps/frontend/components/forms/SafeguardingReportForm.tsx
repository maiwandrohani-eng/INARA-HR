'use client'

import { useState } from 'react'
import { API_BASE_URL } from '@/lib/api-config'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface SafeguardingReportFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function SafeguardingReportForm({ open, onOpenChange, onSubmitSuccess }: SafeguardingReportFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()

  const [reporterName, setReporterName] = useState('')
  const [reporterEmail, setReporterEmail] = useState('')
  const [reporterPhone, setReporterPhone] = useState('')
  const [incidentType, setIncidentType] = useState('')
  const [severity, setSeverity] = useState('')
  const [incidentDate, setIncidentDate] = useState('')
  const [incidentLocation, setIncidentLocation] = useState('')
  const [involvedPersons, setInvolvedPersons] = useState('')
  const [witnesses, setWitnesses] = useState('')
  const [description, setDescription] = useState('')
  const [actionTaken, setActionTaken] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const reportData = {
        reporter_name: isAnonymous ? 'Anonymous' : reporterName,
        reporter_email: isAnonymous ? '' : reporterEmail,
        reporter_phone: isAnonymous ? '' : reporterPhone,
        incident_type: incidentType,
        severity,
        incident_date: incidentDate,
        incident_location: incidentLocation,
        involved_persons: involvedPersons,
        witnesses,
        description,
        action_taken: actionTaken,
        is_anonymous: isAnonymous,
        status: 'reported',
      }

      const token = localStorage.getItem('access_token')
      
      if (!token) {
        alert('You are not logged in. Please log in and try again.')
        return
      }
      
      const response = await fetch(`${API_BASE_URL}/safeguarding/cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(reportData),
      })

      if (!response.ok) {
        if (response.status === 401) {
          alert('Your session has expired. Please log out and log back in.')
          return
        }
        const errorData = await response.json().catch(() => ({}))
        console.error('Error response:', errorData)
        throw new Error('Failed to submit safeguarding report')
      }

      const result = await response.json()
      alert(`Safeguarding report submitted successfully.\nCase Number: ${result.case_number}`)
      resetForm()
      onOpenChange(false)
      if (onSubmitSuccess) {
        onSubmitSuccess()
      }
    } catch (error) {
      console.error('Error submitting safeguarding report:', error)
      alert('Failed to submit report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setReporterName('')
    setReporterEmail('')
    setReporterPhone('')
    setIncidentType('')
    setSeverity('')
    setIncidentDate('')
    setIncidentLocation('')
    setInvolvedPersons('')
    setWitnesses('')
    setDescription('')
    setActionTaken('')
    setIsAnonymous(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-red-600">
            Report Safeguarding Case
          </DialogTitle>
          <DialogDescription className="text-sm">
            <strong>CONFIDENTIAL:</strong> All safeguarding reports are treated with the highest level of confidentiality.
            Your report will be reviewed by authorized personnel only.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Anonymous Reporting Option */}
          <div className="flex items-center space-x-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <input
              type="checkbox"
              id="anonymous"
              checked={isAnonymous}
              onChange={(e) => setIsAnonymous(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="anonymous" className="text-sm font-medium cursor-pointer">
              Submit this report anonymously
            </Label>
          </div>

          {/* Reporter Information */}
          {!isAnonymous && (
            <div className="border rounded-lg p-4 space-y-4">
              <h3 className="font-semibold text-lg">Reporter Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="reporter-name">Your Name *</Label>
                  <Input
                    id="reporter-name"
                    value={reporterName}
                    onChange={(e) => setReporterName(e.target.value)}
                    placeholder="Full name"
                    required={!isAnonymous}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reporter-email">Email</Label>
                  <Input
                    id="reporter-email"
                    type="email"
                    value={reporterEmail}
                    onChange={(e) => setReporterEmail(e.target.value)}
                    placeholder="email@example.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reporter-phone">Phone</Label>
                  <Input
                    id="reporter-phone"
                    type="tel"
                    value={reporterPhone}
                    onChange={(e) => setReporterPhone(e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Incident Details */}
          <div className="border rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-lg">Incident Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="incident-type">Incident Type *</Label>
                <Select value={incidentType} onValueChange={setIncidentType} required>
                  <SelectTrigger id="incident-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="child-abuse">Child Abuse</SelectItem>
                    <SelectItem value="sexual-harassment">Sexual Harassment</SelectItem>
                    <SelectItem value="discrimination">Discrimination</SelectItem>
                    <SelectItem value="bullying">Bullying</SelectItem>
                    <SelectItem value="exploitation">Exploitation</SelectItem>
                    <SelectItem value="neglect">Neglect</SelectItem>
                    <SelectItem value="violence">Violence</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="severity">Severity Level *</Label>
                <Select value={severity} onValueChange={setSeverity} required>
                  <SelectTrigger id="severity">
                    <SelectValue placeholder="Select severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="critical">Critical - Immediate Danger</SelectItem>
                    <SelectItem value="high">High - Serious Concern</SelectItem>
                    <SelectItem value="medium">Medium - Moderate Concern</SelectItem>
                    <SelectItem value="low">Low - Minor Concern</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="incident-date">Date of Incident *</Label>
                <Input
                  id="incident-date"
                  type="date"
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="incident-location">Location *</Label>
                <Input
                  id="incident-location"
                  value={incidentLocation}
                  onChange={(e) => setIncidentLocation(e.target.value)}
                  placeholder="Where did this occur?"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="involved-persons">Persons Involved *</Label>
              <Textarea
                id="involved-persons"
                value={involvedPersons}
                onChange={(e) => setInvolvedPersons(e.target.value)}
                rows={2}
                placeholder="Names and roles of persons involved..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="witnesses">Witnesses (if any)</Label>
              <Textarea
                id="witnesses"
                value={witnesses}
                onChange={(e) => setWitnesses(e.target.value)}
                rows={2}
                placeholder="Names of any witnesses..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Detailed Description *</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                placeholder="Please provide a detailed description of what happened, including dates, times, and any relevant context..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="action-taken">Action Taken (if any)</Label>
              <Textarea
                id="action-taken"
                value={actionTaken}
                onChange={(e) => setActionTaken(e.target.value)}
                rows={3}
                placeholder="Describe any immediate action taken or support provided..."
              />
            </div>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800">
            <strong>Important:</strong> If this is an emergency or someone is in immediate danger, 
            please contact your country's emergency services number or your local safeguarding officer immediately.
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? 'Submitting...' : 'Submit Report'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
