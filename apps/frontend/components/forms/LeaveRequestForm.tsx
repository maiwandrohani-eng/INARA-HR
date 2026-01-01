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

interface LeaveRequestFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LeaveRequestForm({ open, onOpenChange }: LeaveRequestFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()

  // Employee Information
  const [employeeId, setEmployeeId] = useState('')
  const [employeeName, setEmployeeName] = useState('')
  const [position, setPosition] = useState('')
  const [dateHired, setDateHired] = useState('')
  const [idNumber, setIdNumber] = useState('')

  // Leave Details
  const [leaveStartDate, setLeaveStartDate] = useState('')
  const [leaveEndDate, setLeaveEndDate] = useState('')
  const [reason, setReason] = useState('')
  const [dateSubmitted, setDateSubmitted] = useState(new Date().toISOString().split('T')[0])
  const [natureOfLeave, setNatureOfLeave] = useState('')
  const [otherLeaveType, setOtherLeaveType] = useState('')

  // Leave Balance
  const [availableAccruedLeave, setAvailableAccruedLeave] = useState(0)
  const [leaveRequested, setLeaveRequested] = useState(0)
  const [balanceLeave, setBalanceLeave] = useState(0)

  // Supervisor Comment
  const [supervisorComment, setSupervisorComment] = useState('')

  const selectedEmployee = employees.find(emp => emp.id === employeeId)

  // Auto-fill employee details when selected
  useEffect(() => {
    if (selectedEmployee) {
      setEmployeeName(getEmployeeFullName(selectedEmployee))
      // Use job_title or position field instead of position_id UUID
      setPosition(selectedEmployee.job_title || selectedEmployee.position || '')
      setDateHired(selectedEmployee.hire_date || '')
      setIdNumber(selectedEmployee.employee_number || '')
    }
  }, [selectedEmployee])

  // Calculate leave requested and balance when dates change
  useEffect(() => {
    if (leaveStartDate && leaveEndDate) {
      const start = new Date(leaveStartDate)
      const end = new Date(leaveEndDate)
      const diffTime = Math.abs(end.getTime() - start.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1 // +1 to include both start and end dates
      setLeaveRequested(diffDays)
      setBalanceLeave(availableAccruedLeave - diffDays)
    }
  }, [leaveStartDate, leaveEndDate, availableAccruedLeave])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Map frontend fields to backend schema
      // Backend expects: leave_type, start_date, end_date, reason, notes, employee_id (optional)
      const leaveType = natureOfLeave === 'Other' ? otherLeaveType : natureOfLeave
      
      if (!leaveType) {
        alert('Please select a leave type')
        setLoading(false)
        return
      }
      
      if (!leaveStartDate || !leaveEndDate) {
        alert('Please select both start and end dates')
        setLoading(false)
        return
      }

      const leaveData = {
        leave_type: leaveType,
        start_date: leaveStartDate, // Backend expects start_date (not leave_start_date)
        end_date: leaveEndDate, // Backend expects end_date (not leave_end_date)
        reason: reason || undefined,
        notes: supervisorComment || undefined, // Map supervisor_comment to notes
        // employee_id is optional - backend will use current_user if not provided
        employee_id: employeeId || undefined,
      }

      console.log('Submitting leave request with data:', leaveData)

      // Use API client instead of direct fetch for consistent error handling
      const { api } = await import('@/lib/api-client')
      
      try {
        const response = await api.post('/leave/requests', leaveData)
        console.log('Leave request submitted successfully:', response)
        alert('Leave request submitted successfully!')
        onOpenChange(false)
        resetForm()
      } catch (apiError: any) {
        console.error('API Error details:', {
          message: apiError.message,
          response: apiError.response?.data,
          status: apiError.response?.status,
        })
        throw apiError // Re-throw to be caught by outer catch
      }
    } catch (error: any) {
      console.error('Error submitting leave request:', error)
      let errorMsg = 'Unknown error'
      
      if (error.response?.data) {
        // Axios error with response
        const errorDetail = error.response.data.detail || error.response.data.message
        if (Array.isArray(errorDetail)) {
          // Validation errors
          errorMsg = errorDetail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
        } else {
          errorMsg = errorDetail || JSON.stringify(error.response.data)
        }
      } else if (error.message) {
        // Other error with message
        errorMsg = error.message
      }
      
      alert(`Failed to submit leave request: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setEmployeeName('')
    setPosition('')
    setDateHired('')
    setIdNumber('')
    setLeaveStartDate('')
    setLeaveEndDate('')
    setReason('')
    setDateSubmitted(new Date().toISOString().split('T')[0])
    setNatureOfLeave('')
    setOtherLeaveType('')
    setAvailableAccruedLeave(0)
    setLeaveRequested(0)
    setBalanceLeave(0)
    setSupervisorComment('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex justify-center mb-4">
            <img src="/logo.png" alt="INARA Logo" className="h-16 w-16 object-contain" />
          </div>
          <DialogTitle className="text-3xl font-bold text-center">LEAVE REQUEST FORM</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Employee Information Section */}
          <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
            <div className="space-y-2">
              <Label htmlFor="employee">Employee Name *</Label>
              <Select value={employeeId} onValueChange={setEmployeeId} required>
                <SelectTrigger id="employee">
                  <SelectValue placeholder={employeesLoading ? "Loading..." : "Select employee"} />
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

            <div className="space-y-2">
              <Label htmlFor="date-hired">Date Hired</Label>
              <Input
                id="date-hired"
                type="date"
                value={dateHired}
                onChange={(e) => setDateHired(e.target.value)}
                disabled
                className="bg-gray-50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Input
                id="position"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                placeholder="Position"
                disabled
                className="bg-gray-50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="id-number">ID Number</Label>
              <Input
                id="id-number"
                value={idNumber}
                onChange={(e) => setIdNumber(e.target.value)}
                placeholder="ID Number"
                disabled
                className="bg-gray-50"
              />
            </div>
          </div>

          {/* Leave Details Section */}
          <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
            <div className="space-y-2">
              <Label htmlFor="leave-start-date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Leave Start Date *
              </Label>
              <Input
                id="leave-start-date"
                type="date"
                value={leaveStartDate}
                onChange={(e) => setLeaveStartDate(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="leave-end-date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Leave End Date *
              </Label>
              <Input
                id="leave-end-date"
                type="date"
                value={leaveEndDate}
                onChange={(e) => setLeaveEndDate(e.target.value)}
                required
                min={leaveStartDate}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="reason">Reason for Leave *</Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                placeholder="Please provide a reason for your leave..."
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="date-submitted">Date Submitted</Label>
              <Input
                id="date-submitted"
                type="date"
                value={dateSubmitted}
                onChange={(e) => setDateSubmitted(e.target.value)}
                disabled
                className="bg-gray-50"
              />
            </div>
          </div>

          {/* Nature of Leave Section */}
          <div className="p-4 border rounded-lg space-y-4">
            <Label htmlFor="nature-of-leave" className="text-lg font-semibold">Nature of Leave *</Label>
            <Select value={natureOfLeave} onValueChange={setNatureOfLeave} required>
              <SelectTrigger id="nature-of-leave">
                <SelectValue placeholder="Choose from menu" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Annual/Vacation">Annual/Vacation</SelectItem>
                <SelectItem value="Sick">Sick</SelectItem>
                <SelectItem value="Compassionate">Compassionate</SelectItem>
                <SelectItem value="Parental">Parental</SelectItem>
                <SelectItem value="Compensatory">Compensatory</SelectItem>
                <SelectItem value="Leave without pay">Leave without pay</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>

            {natureOfLeave === 'Other' && (
              <div className="space-y-2">
                <Label htmlFor="other-leave-type">Other (Specify) *</Label>
                <Input
                  id="other-leave-type"
                  value={otherLeaveType}
                  onChange={(e) => setOtherLeaveType(e.target.value)}
                  placeholder="Please specify..."
                  required
                />
              </div>
            )}
          </div>

          {/* Leave Balance Section */}
          <div className="p-4 border rounded-lg bg-yellow-50">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="available-leave">Available Accrued Leave (Days)</Label>
                <Input
                  id="available-leave"
                  type="number"
                  value={availableAccruedLeave}
                  onChange={(e) => setAvailableAccruedLeave(Number(e.target.value))}
                  min="0"
                  placeholder="0"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="leave-requested">Leave Requested (Days)</Label>
                <Input
                  id="leave-requested"
                  type="number"
                  value={leaveRequested}
                  disabled
                  className="bg-gray-100 font-semibold"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="balance-leave">Balance Leave (Days)</Label>
                <Input
                  id="balance-leave"
                  type="number"
                  value={balanceLeave}
                  disabled
                  className="bg-gray-100 font-semibold"
                />
              </div>
            </div>
          </div>

          {/* Supervisor Comment Section */}
          <div className="space-y-2 p-4 border rounded-lg">
            <Label htmlFor="supervisor-comment">Supervisor's comment if leave cannot be granted:</Label>
            <Textarea
              id="supervisor-comment"
              value={supervisorComment}
              onChange={(e) => setSupervisorComment(e.target.value)}
              rows={3}
              placeholder="Supervisor comments (optional)..."
              className="bg-gray-50"
            />
          </div>

          {/* Approval Section */}
          <div className="p-4 border rounded-lg bg-gray-50">
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-green-500 text-white text-center py-2 font-semibold rounded">
                  Approved
                </div>
                <input type="checkbox" className="h-5 w-5" disabled />
              </div>
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-red-500 text-white text-center py-2 font-semibold rounded">
                  Declined
                </div>
                <input type="checkbox" className="h-5 w-5" disabled />
              </div>
            </div>

            <div className="space-y-2 border-t pt-4">
              <div className="grid grid-cols-4 gap-4 font-semibold bg-white p-2 border">
                <div>Position</div>
                <div>Name</div>
                <div>Signature</div>
                <div>Date</div>
              </div>

              <div className="grid grid-cols-4 gap-4 p-2 border bg-white">
                <div className="font-medium">HR</div>
                <div className="text-gray-400">Pending</div>
                <div className="text-gray-400">Pending</div>
                <div className="text-gray-400">Pending</div>
              </div>

              <div className="grid grid-cols-4 gap-4 p-2 border bg-white">
                <div className="font-medium">Immediate Supervisor</div>
                <div className="text-gray-400">Pending</div>
                <div className="text-gray-400">Pending</div>
                <div className="text-gray-400">Pending</div>
              </div>

              <div className="grid grid-cols-4 gap-4 p-2 border bg-white">
                <div className="font-medium">Country Director</div>
                <div className="text-gray-400 text-sm">(if leave exceeds balance)</div>
                <div className="text-gray-400">Pending</div>
                <div className="text-gray-400">Pending</div>
              </div>
            </div>
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
              {loading ? 'Submitting...' : 'Submit Request'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
