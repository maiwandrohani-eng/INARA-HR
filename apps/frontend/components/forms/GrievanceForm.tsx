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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Calendar } from 'lucide-react'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface GrievanceFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function GrievanceForm({ open, onOpenChange, onSubmitSuccess }: GrievanceFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()

  const [employeeId, setEmployeeId] = useState('')
  const [grievanceType, setGrievanceType] = useState('')
  const [relatedPerson, setRelatedPerson] = useState('')
  const [relationshipToComplainant, setRelationshipToComplainant] = useState('')
  const [incidentDate, setIncidentDate] = useState('')
  const [description, setDescription] = useState('')
  const [previousAttempts, setPreviousAttempts] = useState('')
  const [desiredResolution, setDesiredResolution] = useState('')
  const [witnesses, setWitnesses] = useState('')
  const [isConfidential, setIsConfidential] = useState(false)

  const selectedEmployee = employees.find(emp => emp.id === employeeId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const grievanceData = {
        employee_id: employeeId,
        employee_name: selectedEmployee ? getEmployeeFullName(selectedEmployee) : '',
        grievance_type: grievanceType,
        related_person: relatedPerson,
        relationship_to_complainant: relationshipToComplainant,
        incident_date: incidentDate,
        description: description,
        previous_attempts: previousAttempts,
        desired_resolution: desiredResolution,
        witnesses: witnesses,
        is_confidential: isConfidential,
        status: 'pending',
      }

      const token = localStorage.getItem('access_token')
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${baseUrl}/grievances/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(grievanceData),
      })

      if (!response.ok) {
        throw new Error('Failed to submit grievance')
      }

      alert('Grievance submitted successfully!')
      onOpenChange(false)
      resetForm()
      if (onSubmitSuccess) {
        onSubmitSuccess()
      }
    } catch (error) {
      console.error('Error submitting grievance:', error)
      alert('Failed to submit grievance. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setGrievanceType('')
    setRelatedPerson('')
    setRelationshipToComplainant('')
    setIncidentDate('')
    setDescription('')
    setPreviousAttempts('')
    setDesiredResolution('')
    setWitnesses('')
    setIsConfidential(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">File Grievance</DialogTitle>
          <DialogDescription>
            Submit a formal grievance for review and resolution
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Confidentiality Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Confidential Process:</strong> All grievances are handled with strict confidentiality. 
              Information will only be shared with those who need to know to resolve the matter.
            </p>
          </div>

          {/* Complainant Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Complainant Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2 col-span-2">
                <Label htmlFor="employee">Employee *</Label>
                <Select value={employeeId} onValueChange={setEmployeeId} required>
                  <SelectTrigger id="employee">
                    <SelectValue placeholder={employeesLoading ? "Loading..." : "Select employee"} />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.employee_number} - {getEmployeeFullName(emp)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedEmployee && (
                <>
                  <div className="space-y-2">
                    <Label>Position</Label>
                    <Input value={selectedEmployee.position_id || 'N/A'} readOnly className="bg-gray-50" />
                  </div>
                  <div className="space-y-2">
                    <Label>Location</Label>
                    <Input value={selectedEmployee.work_location || 'N/A'} readOnly className="bg-gray-50" />
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Grievance Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Grievance Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="grievance-type">Type of Grievance *</Label>
                <Select value={grievanceType} onValueChange={setGrievanceType} required>
                  <SelectTrigger id="grievance-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="harassment">Harassment</SelectItem>
                    <SelectItem value="discrimination">Discrimination</SelectItem>
                    <SelectItem value="unfair_treatment">Unfair Treatment</SelectItem>
                    <SelectItem value="working_conditions">Working Conditions</SelectItem>
                    <SelectItem value="safety_concerns">Safety Concerns</SelectItem>
                    <SelectItem value="compensation">Compensation & Benefits</SelectItem>
                    <SelectItem value="workload">Excessive Workload</SelectItem>
                    <SelectItem value="manager_conduct">Manager Conduct</SelectItem>
                    <SelectItem value="policy_violation">Policy Violation</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="incident-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Date of Incident *
                </Label>
                <Input
                  id="incident-date"
                  type="date"
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="related-person">Person Involved (if applicable)</Label>
                <Input
                  id="related-person"
                  value={relatedPerson}
                  onChange={(e) => setRelatedPerson(e.target.value)}
                  placeholder="Name of person involved"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="relationship">Relationship to Complainant</Label>
                <Select value={relationshipToComplainant} onValueChange={setRelationshipToComplainant}>
                  <SelectTrigger id="relationship">
                    <SelectValue placeholder="Select relationship" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="supervisor">Direct Supervisor</SelectItem>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="colleague">Colleague</SelectItem>
                    <SelectItem value="subordinate">Subordinate</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="na">N/A</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Detailed Description *</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                placeholder="Please provide a detailed description of the grievance, including what happened, when, where, and who was involved..."
                required
              />
              <p className="text-xs text-gray-500">
                Be as specific as possible. Include dates, times, locations, and any relevant details.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="previous-attempts">Previous Resolution Attempts (Optional)</Label>
              <Textarea
                id="previous-attempts"
                value={previousAttempts}
                onChange={(e) => setPreviousAttempts(e.target.value)}
                rows={3}
                placeholder="Have you tried to resolve this issue before? If so, please describe what steps you took..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="witnesses">Witnesses (if any)</Label>
              <Textarea
                id="witnesses"
                value={witnesses}
                onChange={(e) => setWitnesses(e.target.value)}
                rows={2}
                placeholder="Names and contact information of any witnesses..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="desired-resolution">Desired Resolution *</Label>
              <Textarea
                id="desired-resolution"
                value={desiredResolution}
                onChange={(e) => setDesiredResolution(e.target.value)}
                rows={3}
                placeholder="What outcome or resolution are you seeking?"
                required
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="confidential"
                checked={isConfidential}
                onChange={(e) => setIsConfidential(e.target.checked)}
                className="rounded border-gray-300"
              />
              <Label htmlFor="confidential" className="text-sm font-normal cursor-pointer">
                Mark as highly confidential (restrict access to HR leadership only)
              </Label>
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-sm text-yellow-800">
              <strong>Please Note:</strong> Filing a grievance is a serious step. False accusations may result in disciplinary action. 
              We encourage you to discuss concerns with your supervisor or HR before filing a formal grievance when appropriate.
            </p>
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
              className="bg-gradient-to-r from-pink-600 to-cyan-600 hover:from-pink-700 hover:to-cyan-700"
            >
              {loading ? 'Submitting...' : 'Submit Grievance'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
