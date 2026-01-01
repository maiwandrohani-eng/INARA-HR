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
import { Calendar, Plane } from 'lucide-react'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface TravelRequestFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmitSuccess?: () => void
}

export function TravelRequestForm({ open, onOpenChange, onSubmitSuccess }: TravelRequestFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()

  const [employeeId, setEmployeeId] = useState('')
  const [employeeName, setEmployeeName] = useState('')
  const [employeeNumber, setEmployeeNumber] = useState('')
  const [department, setDepartment] = useState('')
  const [position, setPosition] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  
  // Travel Details - Multiple segments
  const [travelSegments, setTravelSegments] = useState([
    { from: '', to: '', startDate: '', endDate: '', mode: '' }
  ])
  
  const [purpose, setPurpose] = useState('')
  
  // Estimated Expenses
  const [airfare, setAirfare] = useState('')
  const [airfareAttachment, setAirfareAttachment] = useState('')
  const [accommodation, setAccommodation] = useState('')
  const [accommodationCost, setAccommodationCost] = useState('')
  const [accommodationAttachment, setAccommodationAttachment] = useState('')
  const [mealsPerDiem, setMealsPerDiem] = useState('')
  const [transportation, setTransportation] = useState('')
  const [otherExpenses, setOtherExpenses] = useState('')
  const [budgetLine, setBudgetLine] = useState('')
  const [budgetCode, setBudgetCode] = useState('')
  
  // Travel Itinerary (to be confirmed after approval)
  const [departureFlight, setDepartureFlight] = useState('')
  const [returnFlight, setReturnFlight] = useState('')
  const [rentalCar, setRentalCar] = useState('')
  const [otherTransport, setOtherTransport] = useState('')
  const [meetingSchedule, setMeetingSchedule] = useState('')
  
  // Approval and Authorization
  const [approverName, setApproverName] = useState('')
  const [approvalDate, setApprovalDate] = useState('')
  const [signature, setSignature] = useState('')

  const selectedEmployee = employees.find(emp => emp.id === employeeId)

  const addTravelSegment = () => {
    setTravelSegments([...travelSegments, { from: '', to: '', startDate: '', endDate: '', mode: '' }])
  }

  const removeTravelSegment = (index: number) => {
    if (travelSegments.length > 1) {
      setTravelSegments(travelSegments.filter((_, i) => i !== index))
    }
  }

  const updateTravelSegment = (index: number, field: string, value: string) => {
    const updated = [...travelSegments]
    updated[index] = { ...updated[index], [field]: value }
    setTravelSegments(updated)
  }

  const calculateTotalExpenses = () => {
    const total = 
      parseFloat(airfare || '0') +
      parseFloat(accommodationCost || '0') +
      parseFloat(mealsPerDiem || '0') +
      parseFloat(transportation || '0') +
      parseFloat(otherExpenses || '0')
    return total.toFixed(2)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const travelData = {
        employee_id: employeeId,
        employee_name: selectedEmployee ? getEmployeeFullName(selectedEmployee) : employeeName,
        employee_number: selectedEmployee?.employee_number || employeeNumber,
        department: selectedEmployee?.work_location || department,
        position: selectedEmployee?.position_id || position,
        email: selectedEmployee?.work_email || email,
        phone: selectedEmployee?.phone || phone,
        
        travel_segments: travelSegments,
        purpose: purpose,
        
        // Estimated Expenses
        airfare: parseFloat(airfare || '0'),
        airfare_attachment: airfareAttachment,
        accommodation: accommodation,
        accommodation_cost: parseFloat(accommodationCost || '0'),
        accommodation_attachment: accommodationAttachment,
        meals_per_diem: mealsPerDiem,
        transportation: parseFloat(transportation || '0'),
        other_expenses: parseFloat(otherExpenses || '0'),
        total_estimated_expenses: parseFloat(calculateTotalExpenses()),
        budget_line: budgetLine,
        budget_code: budgetCode,
        
        // Travel Itinerary
        departure_flight: departureFlight,
        return_flight: returnFlight,
        rental_car: rentalCar,
        other_transport: otherTransport,
        meeting_schedule: meetingSchedule,
        
        // Approval
        approver_name: approverName,
        approval_date: approvalDate,
        signature: signature,
        
        status: 'pending',
      }

      const token = localStorage.getItem('access_token')
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${baseUrl}/travel/requests/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(travelData),
      })

      if (!response.ok) {
        throw new Error('Failed to submit travel request')
      }

      alert('Travel request submitted successfully!')
      onOpenChange(false)
      resetForm()
      if (onSubmitSuccess) {
        onSubmitSuccess()
      }
    } catch (error) {
      console.error('Error submitting travel request:', error)
      alert('Failed to submit travel request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setEmployeeName('')
    setEmployeeNumber('')
    setDepartment('')
    setPosition('')
    setEmail('')
    setPhone('')
    setTravelSegments([{ from: '', to: '', startDate: '', endDate: '', mode: '' }])
    setPurpose('')
    setAirfare('')
    setAirfareAttachment('')
    setAccommodation('')
    setAccommodationCost('')
    setAccommodationAttachment('')
    setMealsPerDiem('')
    setTransportation('')
    setOtherExpenses('')
    setBudgetLine('')
    setBudgetCode('')
    setDepartureFlight('')
    setReturnFlight('')
    setRentalCar('')
    setOtherTransport('')
    setMeetingSchedule('')
    setApproverName('')
    setApprovalDate('')
    setSignature('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Plane className="h-6 w-6" />
            New Travel Request
          </DialogTitle>
          <DialogDescription>
            Submit a travel request for international or domestic travel
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 1. Employee Information */}
          <div className="space-y-4 border-b pb-4">
            <h3 className="text-lg font-semibold text-gray-900">1. Employee Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2 col-span-2">
                <Label htmlFor="employee">Employee Name *</Label>
                <Select 
                  value={employeeId} 
                  onValueChange={(value) => {
                    setEmployeeId(value)
                    const emp = employees.find(e => e.id === value)
                    if (emp) {
                      setEmployeeName(getEmployeeFullName(emp))
                      setEmployeeNumber(emp.employee_number || '')
                      setDepartment(emp.work_location || '')
                      setEmail(emp.work_email || '')
                      setPhone(emp.phone || '')
                    }
                  }} 
                  required
                >
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

              <div className="space-y-2">
                <Label htmlFor="employee-id">Employee ID</Label>
                <Input 
                  id="employee-id" 
                  value={selectedEmployee?.employee_number || employeeNumber} 
                  onChange={(e) => setEmployeeNumber(e.target.value)}
                  readOnly={!!selectedEmployee}
                  className={selectedEmployee ? "bg-gray-50" : ""} 
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department/Division</Label>
                <Input 
                  id="department" 
                  value={selectedEmployee?.work_location || department} 
                  onChange={(e) => setDepartment(e.target.value)}
                  readOnly={!!selectedEmployee}
                  className={selectedEmployee ? "bg-gray-50" : ""} 
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Position/Title</Label>
                <Input 
                  id="position" 
                  value={position} 
                  onChange={(e) => setPosition(e.target.value)}
                  placeholder="CEO, Manager, etc."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input 
                  id="email" 
                  type="email"
                  value={selectedEmployee?.work_email || email} 
                  onChange={(e) => setEmail(e.target.value)}
                  readOnly={!!selectedEmployee}
                  className={selectedEmployee ? "bg-gray-50" : ""} 
                />
              </div>

              <div className="space-y-2 col-span-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input 
                  id="phone" 
                  value={selectedEmployee?.phone || phone} 
                  onChange={(e) => setPhone(e.target.value)}
                  readOnly={!!selectedEmployee}
                  className={selectedEmployee ? "bg-gray-50" : ""} 
                />
              </div>
            </div>
          </div>

          {/* 2. Travel Details */}
          <div className="space-y-4 border-b pb-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">2. Travel Details</h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addTravelSegment}
                className="text-xs"
              >
                + Add Segment
              </Button>
            </div>
            
            {travelSegments.map((segment, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Segment {index + 1}</span>
                  {travelSegments.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeTravelSegment(index)}
                      className="text-red-600 hover:text-red-700 text-xs"
                    >
                      Remove
                    </Button>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>From</Label>
                    <Input
                      value={segment.from}
                      onChange={(e) => updateTravelSegment(index, 'from', e.target.value)}
                      placeholder="Istanbul"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>To</Label>
                    <Input
                      value={segment.to}
                      onChange={(e) => updateTravelSegment(index, 'to', e.target.value)}
                      placeholder="Ankara"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Travel Start Date</Label>
                    <Input
                      type="date"
                      value={segment.startDate}
                      onChange={(e) => updateTravelSegment(index, 'startDate', e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Travel End Date</Label>
                    <Input
                      type="date"
                      value={segment.endDate}
                      onChange={(e) => updateTravelSegment(index, 'endDate', e.target.value)}
                      min={segment.startDate}
                      required
                    />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label>Mode of Transportation</Label>
                    <Select 
                      value={segment.mode} 
                      onValueChange={(value) => updateTravelSegment(index, 'mode', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select mode" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Road">Road</SelectItem>
                        <SelectItem value="Air">Air</SelectItem>
                        <SelectItem value="Rail">Rail</SelectItem>
                        <SelectItem value="Sea">Sea</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 3. Purpose of Travel */}
          <div className="space-y-4 border-b pb-4">
            <h3 className="text-lg font-semibold text-gray-900">3. Purpose of Travel</h3>
            <div className="space-y-2">
              <Textarea
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                rows={4}
                placeholder="Submit my visa application for a Dutch visa to participate in the Netherlands fundraising event."
                required
              />
            </div>
          </div>

          {/* 4. Estimated Expenses */}
          <div className="space-y-4 border-b pb-4">
            <h3 className="text-lg font-semibold text-gray-900">4. Estimated Expenses</h3>
            
            <div className="space-y-3">
              {/* Airfare */}
              <div className="grid grid-cols-3 gap-4 items-end">
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="airfare">Airfare</Label>
                  <Input
                    id="airfare"
                    type="number"
                    step="0.01"
                    value={airfare}
                    onChange={(e) => setAirfare(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="airfare-attachment" className="text-xs">Attachment Reference</Label>
                  <Input
                    id="airfare-attachment"
                    value={airfareAttachment}
                    onChange={(e) => setAirfareAttachment(e.target.value)}
                    placeholder="e.g., Attachment #1"
                    className="text-sm"
                  />
                </div>
              </div>

              {/* Accommodation */}
              <div className="grid grid-cols-3 gap-4 items-end">
                <div className="space-y-2">
                  <Label htmlFor="accommodation">Accommodation</Label>
                  <Input
                    id="accommodation"
                    value={accommodation}
                    onChange={(e) => setAccommodation(e.target.value)}
                    placeholder="Airbnb cost for two days"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="accommodation-cost">Cost</Label>
                  <Input
                    id="accommodation-cost"
                    type="number"
                    step="0.01"
                    value={accommodationCost}
                    onChange={(e) => setAccommodationCost(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="accommodation-attachment" className="text-xs">Attachment</Label>
                  <Input
                    id="accommodation-attachment"
                    value={accommodationAttachment}
                    onChange={(e) => setAccommodationAttachment(e.target.value)}
                    placeholder="e.g., Attachment #2"
                    className="text-sm"
                  />
                </div>
              </div>

              {/* Meals/Per Diem */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="meals">Meals/Per Diem</Label>
                  <Input
                    id="meals"
                    type="number"
                    step="0.01"
                    value={mealsPerDiem}
                    onChange={(e) => setMealsPerDiem(e.target.value)}
                    placeholder="0.00"
                  />
                  <p className="text-xs text-gray-500">Enter total amount (e.g., Per diem $20/day × 3 days = $60)</p>
                </div>
              </div>

              {/* Transportation */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="transportation">Transportation</Label>
                  <Input
                    id="transportation"
                    type="number"
                    step="0.01"
                    value={transportation}
                    onChange={(e) => setTransportation(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="other-expenses">Other Expenses</Label>
                  <Input
                    id="other-expenses"
                    type="number"
                    step="0.01"
                    value={otherExpenses}
                    onChange={(e) => setOtherExpenses(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Total */}
              <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-4 mt-4">
                <div className="flex justify-between items-center">
                  <Label className="text-lg font-bold text-gray-900">Total Estimated Expenses:</Label>
                  <span className="text-2xl font-bold text-gray-900">$ {calculateTotalExpenses()}</span>
                </div>
              </div>

              {/* Budget Line */}
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="budget-line">Budget Line and Budget Code</Label>
                  <Input
                    id="budget-line"
                    value={budgetLine}
                    onChange={(e) => setBudgetLine(e.target.value)}
                    placeholder="M&E - HCI"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 5. Travel Itinerary */}
          <div className="space-y-4 border-b pb-4">
            <h3 className="text-lg font-semibold text-gray-900">5. Travel Itinerary <span className="text-sm font-normal text-gray-500">(to be confirmed after approval)</span></h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="departure-flight">Departure Flight</Label>
                <Input
                  id="departure-flight"
                  value={departureFlight}
                  onChange={(e) => setDepartureFlight(e.target.value)}
                  placeholder="Flight details"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="return-flight">Return Flight</Label>
                <Input
                  id="return-flight"
                  value={returnFlight}
                  onChange={(e) => setReturnFlight(e.target.value)}
                  placeholder="Flight details"
                />
              </div>

              <div className="space-y-2 col-span-2">
                <Label htmlFor="accommodation-details">Accommodation</Label>
                <Input
                  id="accommodation-details"
                  value={accommodation}
                  onChange={(e) => setAccommodation(e.target.value)}
                  placeholder="Hotel name and address"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="rental-car">Rental Car (if applicable)</Label>
                <Input
                  id="rental-car"
                  value={rentalCar}
                  onChange={(e) => setRentalCar(e.target.value)}
                  placeholder="Car rental details"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="other-transport">Other Transportation</Label>
                <Input
                  id="other-transport"
                  value={otherTransport}
                  onChange={(e) => setOtherTransport(e.target.value)}
                  placeholder="Additional transport details"
                />
              </div>

              <div className="space-y-2 col-span-2">
                <Label htmlFor="meeting-schedule">Meeting/Event Schedule</Label>
                <Textarea
                  id="meeting-schedule"
                  value={meetingSchedule}
                  onChange={(e) => setMeetingSchedule(e.target.value)}
                  rows={3}
                  placeholder="Meeting dates, times, and locations"
                />
              </div>
            </div>
          </div>

          {/* 6. Employee Declaration */}
          <div className="space-y-4 border-b pb-4">
            <h3 className="text-lg font-semibold text-gray-900">6. Employee Declaration</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                <li>I request approval for the above travel plans and expenses.</li>
                <li>I certify that the information provided is accurate to the best of my knowledge.</li>
                <li>I understand and agree to comply with the INARA's travel policies and guidelines.</li>
                <li>I will submit all necessary receipts and expense reports promptly upon my return.</li>
              </ul>
              <p className="mt-4 text-gray-700">
                By signing below, I acknowledge that I have read, understood, and agreed to the terms and conditions outlined in this travel authorization form.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="signature">Signature</Label>
                <Input
                  id="signature"
                  value={signature}
                  onChange={(e) => setSignature(e.target.value)}
                  placeholder="Type your full name"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="signature-date">Date</Label>
                <Input
                  id="signature-date"
                  type="date"
                  value={approvalDate}
                  onChange={(e) => setApprovalDate(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>

          {/* 7. Approval and Authorization */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">7. Approval and Authorization</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2 col-span-2">
                <Label htmlFor="approver-name">Supervisor/Manager Name *</Label>
                <Input
                  id="approver-name"
                  value={approverName}
                  onChange={(e) => setApproverName(e.target.value)}
                  placeholder="e.g., Arwa Damon"
                  required
                />
              </div>
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Please submit travel requests at least 2 weeks in advance for domestic travel 
              and 4 weeks for international travel to allow for proper arrangements and approvals.
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
              {loading ? 'Submitting...' : 'Submit Request'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
