'use client'

export const dynamic = "force-dynamic";

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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
import { ArrowLeft } from 'lucide-react'
import { Employee } from '@/hooks/useEmployees'
import apiClient, { api } from '@/lib/api-client'

interface Department {
  id: string
  name: string
}

interface Position {
  id: string
  title: string
}

export default function EditEmployeePage() {
  const params = useParams()
  const router = useRouter()
  const [employee, setEmployee] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Form fields - All fields from Add Employee form
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [workEmail, setWorkEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [mobile, setMobile] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [gender, setGender] = useState('')
  const [nationality, setNationality] = useState('')
  const [countryCode, setCountryCode] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [workLocation, setWorkLocation] = useState('')
  const [hireDate, setHireDate] = useState('')
  const [positionId, setPositionId] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [managerId, setManagerId] = useState('')

  // Additional details
  const [nationalId, setNationalId] = useState('')
  const [passportNumber, setPassportNumber] = useState('')

  // Emergency contacts
  const [emergencyContactName, setEmergencyContactName] = useState('')
  const [emergencyContactPhone, setEmergencyContactPhone] = useState('')
  const [emergencyContactRelationship, setEmergencyContactRelationship] = useState('')

  const [emergencyContact2Name, setEmergencyContact2Name] = useState('')
  const [emergencyContact2Phone, setEmergencyContact2Phone] = useState('')
  const [emergencyContact2Relationship, setEmergencyContact2Relationship] = useState('')
  const [emergencyContact2Note, setEmergencyContact2Note] = useState('')

  // Medical & work type
  const [bloodType, setBloodType] = useState('')
  const [medicalConditions, setMedicalConditions] = useState('')
  const [workType, setWorkType] = useState('')

  // Data for dropdowns
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [positions, setPositions] = useState<Position[]>([])

  useEffect(() => {
    fetchEmployee()
    fetchEmployees()
    fetchDepartments()
    fetchPositions()
  }, [params.id])

  const fetchEmployees = async () => {
    try {
      const data = await api.get('/employees/')
      setEmployees(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching employees:', error)
    }
  }

  const fetchDepartments = async () => {
    try {
      const data = await api.get('/employees/departments')
      setDepartments(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching departments:', error)
    }
  }

  const fetchPositions = async () => {
    try {
      const data = await api.get('/employees/positions')
      setPositions(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching positions:', error)
    }
  }

  const fetchEmployee = async () => {
    try {
      // Add timestamp to prevent caching
      const data = await api.get(`/employees/${params.id}?t=${Date.now()}`)
      setEmployee(data)
      // Populate all form fields
      setFirstName(data.first_name || '')
      setLastName(data.last_name || '')
      setWorkEmail(data.work_email || '')
      setPhone(data.phone || '')
      setMobile(data.mobile || '')
      setDateOfBirth(data.date_of_birth || '')
      setGender(data.gender || '')
      setNationality(data.nationality || '')
      setCountryCode(data.country_code || '')
      setEmploymentType(data.employment_type || '')
      setWorkLocation(data.work_location || '')
      setHireDate(data.hire_date || '')
      setPositionId(data.position_id || '')
      setDepartmentId(data.department_id || '')
      setManagerId(data.manager_id || '')
      setNationalId(data.national_id || '')
      setPassportNumber(data.passport_number || '')
      setEmergencyContactName(data.emergency_contact_name || '')
      setEmergencyContactPhone(data.emergency_contact_phone || '')
      setEmergencyContactRelationship(data.emergency_contact_relationship || '')
      setEmergencyContact2Name(data.emergency_contact_2_name || '')
      setEmergencyContact2Phone(data.emergency_contact_2_phone || '')
      setEmergencyContact2Relationship(data.emergency_contact_2_relationship || '')
      setEmergencyContact2Note(data.emergency_contact_2_note || '')
      setBloodType(data.blood_type || '')
      setMedicalConditions(data.medical_conditions || '')
      setWorkType(data.work_type || '')
    } catch (error) {
      console.error('Error fetching employee:', error)
      alert('Failed to load employee')
      router.back()
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      await api.patch(`/employees/${params.id}`, {
        first_name: firstName,
        last_name: lastName,
        work_email: workEmail,
        phone: phone || null,
        mobile: mobile || null,
        date_of_birth: dateOfBirth || null,
        gender: gender || null,
        nationality: nationality || null,
        country_code: countryCode || null,
        employment_type: employmentType || null,
        work_location: workLocation || null,
        hire_date: hireDate || null,
        position_id: positionId || null,
        department_id: departmentId || null,
        manager_id: (managerId && managerId !== 'none') ? managerId : null,
        national_id: nationalId || null,
        passport_number: passportNumber || null,
        emergency_contact_name: emergencyContactName || null,
        emergency_contact_phone: emergencyContactPhone || null,
        emergency_contact_relationship: emergencyContactRelationship || null,
        emergency_contact_2_name: emergencyContact2Name || null,
        emergency_contact_2_phone: emergencyContact2Phone || null,
        emergency_contact_2_relationship: emergencyContact2Relationship || null,
        emergency_contact_2_note: emergencyContact2Note || null,
        blood_type: bloodType || null,
        medical_conditions: medicalConditions || null,
        work_type: workType || null,
      })

      alert('Employee updated successfully')
      // Force a hard refresh to clear any cached data
      router.push(`/dashboard/employees/${params.id}`)
      router.refresh()
    } catch (error: any) {
      console.error('Error updating employee:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Failed to update employee'
      alert(`Failed to update employee: ${errorMessage}`)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="p-6">Loading...</div>
  }

  if (!employee) {
    return <div className="p-6">Employee not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Edit Employee</h1>
          <p className="text-gray-500 mt-2">{employee.employee_number} - {employee.first_name} {employee.last_name}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Employee Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name *</Label>
                  <Input
                    id="firstName"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name *</Label>
                  <Input
                    id="lastName"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="dateOfBirth">Date of Birth</Label>
                  <Input
                    id="dateOfBirth"
                    type="date"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gender">Gender</Label>
                  <Select value={gender || ''} onValueChange={setGender}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nationality">Nationality</Label>
                  <Input
                    id="nationality"
                    value={nationality}
                    onChange={(e) => setNationality(e.target.value)}
                    placeholder="e.g., AF, US, UK"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="countryCode">Country Code</Label>
                  <Input
                    id="countryCode"
                    value={countryCode}
                    onChange={(e) => setCountryCode(e.target.value)}
                    placeholder="e.g., AF, TR"
                  />
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="workEmail">Work Email *</Label>
                  <Input
                    id="workEmail"
                    type="email"
                    value={workEmail}
                    onChange={(e) => setWorkEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mobile">Mobile</Label>
                  <Input
                    id="mobile"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Emergency Contacts */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Emergency Contacts</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Primary Emergency Contact</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="emergency-name">Contact Name</Label>
                      <Input
                        id="emergency-name"
                        value={emergencyContactName}
                        onChange={(e) => setEmergencyContactName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergency-phone">Contact Phone</Label>
                      <Input
                        id="emergency-phone"
                        value={emergencyContactPhone}
                        onChange={(e) => setEmergencyContactPhone(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergency-relationship">Relationship</Label>
                      <Input
                        id="emergency-relationship"
                        value={emergencyContactRelationship}
                        onChange={(e) => setEmergencyContactRelationship(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Secondary Emergency Contact</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="emergency2-name">Contact Name</Label>
                      <Input
                        id="emergency2-name"
                        value={emergencyContact2Name}
                        onChange={(e) => setEmergencyContact2Name(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergency2-phone">Contact Phone</Label>
                      <Input
                        id="emergency2-phone"
                        value={emergencyContact2Phone}
                        onChange={(e) => setEmergencyContact2Phone(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergency2-relationship">Relationship</Label>
                      <Input
                        id="emergency2-relationship"
                        value={emergencyContact2Relationship}
                        onChange={(e) => setEmergencyContact2Relationship(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="space-y-2 mt-4">
                    <Label htmlFor="emergency2-note">Notes</Label>
                    <Textarea
                      id="emergency2-note"
                      className="min-h-[80px]"
                      value={emergencyContact2Note}
                      onChange={(e) => setEmergencyContact2Note(e.target.value)}
                      placeholder="Additional notes about this emergency contact..."
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Medical & Health Information */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Medical & Health Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bloodType">Blood Type</Label>
                  <Select value={bloodType || ''} onValueChange={setBloodType}>
                    <SelectTrigger id="bloodType">
                      <SelectValue placeholder="Select blood type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A+">A+</SelectItem>
                      <SelectItem value="A-">A-</SelectItem>
                      <SelectItem value="B+">B+</SelectItem>
                      <SelectItem value="B-">B-</SelectItem>
                      <SelectItem value="AB+">AB+</SelectItem>
                      <SelectItem value="AB-">AB-</SelectItem>
                      <SelectItem value="O+">O+</SelectItem>
                      <SelectItem value="O-">O-</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="workType">Type of Work</Label>
                  <Select value={workType || ''} onValueChange={setWorkType}>
                    <SelectTrigger id="workType">
                      <SelectValue placeholder="Select work type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="on_site">On Site</SelectItem>
                      <SelectItem value="remote">Remote</SelectItem>
                      <SelectItem value="hybrid">Hybrid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2 mt-4">
                <Label htmlFor="medicalConditions">Pre-existing Medical Conditions</Label>
                <Textarea
                  id="medicalConditions"
                  className="min-h-[100px]"
                  value={medicalConditions}
                  onChange={(e) => setMedicalConditions(e.target.value)}
                  placeholder="List any pre-existing medical conditions, allergies, or health concerns..."
                />
              </div>
            </div>

            {/* Employment Information */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Employment Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hireDate">Hire Date</Label>
                  <Input
                    id="hireDate"
                    type="date"
                    value={hireDate}
                    onChange={(e) => setHireDate(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="employmentType">Employment Type</Label>
                  <Select value={employmentType || ''} onValueChange={setEmploymentType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select employment type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full_time">Full-Time</SelectItem>
                      <SelectItem value="part_time">Part-Time</SelectItem>
                      <SelectItem value="consultant">Consultant</SelectItem>
                      <SelectItem value="volunteer">Volunteer - Paid</SelectItem>
                      <SelectItem value="volunteer">Volunteer - Unpaid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Select value={departmentId || ''} onValueChange={setDepartmentId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept) => (
                        <SelectItem key={dept.id} value={dept.id}>
                          {dept.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="position">Position</Label>
                  <Select value={positionId || ''} onValueChange={setPositionId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select position" />
                    </SelectTrigger>
                    <SelectContent>
                      {positions.map((pos) => (
                        <SelectItem key={pos.id} value={pos.id}>
                          {pos.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="manager">Manager/Supervisor</Label>
                  <Select value={managerId} onValueChange={setManagerId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select manager" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No Manager</SelectItem>
                      {employees.filter(emp => emp.id !== params.id).map((emp) => (
                        <SelectItem key={emp.id} value={emp.id}>
                          {emp.employee_number} - {emp.first_name} {emp.last_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="workLocation">Work Location</Label>
                  <Input
                    id="workLocation"
                    value={workLocation}
                    onChange={(e) => setWorkLocation(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
