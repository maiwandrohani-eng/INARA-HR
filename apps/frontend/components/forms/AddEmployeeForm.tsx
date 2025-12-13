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
import { Calendar } from 'lucide-react'

interface Employee {
  id: string
  first_name: string
  last_name: string
  employee_number: string
}

interface Department {
  id: string
  name: string
}

interface Position {
  id: string
  title: string
}

interface CountryConfig {
  id: string
  country_code: string
  country_name: string
  default_currency: string
  timezone: string
}

interface AddEmployeeFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function AddEmployeeForm({ open, onOpenChange, onSuccess }: AddEmployeeFormProps) {
  const [loading, setLoading] = useState(false)
  
  const [employeeNumber, setEmployeeNumber] = useState('')
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

  // Data for dropdowns
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [countries, setCountries] = useState<CountryConfig[]>([])

  // Fetch employees, departments, positions, and countries when dialog opens
  useEffect(() => {
    if (open) {
      fetchEmployees()
      fetchDepartments()
      fetchPositions()
      fetchCountries()
    }
  }, [open])

  const fetchEmployees = async () => {
    try {
      const token = localStorage.getItem('access_token')
      console.log('Fetching employees for manager dropdown...')
      const response = await fetch('http://localhost:8000/api/v1/employees/', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      console.log('Employees fetch response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('Employees fetched for dropdown:', data.length, 'employees')
        console.log('Employee data:', data)
        setEmployees(data)
      } else {
        const error = await response.text()
        console.error('Failed to fetch employees:', response.status, error)
      }
    } catch (error) {
      console.error('Error fetching employees:', error)
    }
  }

  const fetchDepartments = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/employees/departments', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setDepartments(data)
      }
    } catch (error) {
      console.error('Error fetching departments:', error)
    }
  }

  const fetchPositions = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/employees/positions', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setPositions(data)
      }
    } catch (error) {
      console.error('Error fetching positions:', error)
    }
  }

  const fetchCountries = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/admin/countries', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setCountries(data)
      }
    } catch (error) {
      console.error('Error fetching countries:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Validate required fields
      if (!firstName || !lastName || !workEmail || !employmentType || !hireDate) {
        alert('Please fill in all required fields: First Name, Last Name, Email, Employment Type, and Hire Date')
        setLoading(false)
        return
      }

      const employeeData = {
        employee_number: employeeNumber || null,  // Let backend auto-generate if empty
        first_name: firstName,
        last_name: lastName,
        work_email: workEmail,
        phone: phone || null,
        mobile: mobile || null,
        date_of_birth: dateOfBirth || null,
        gender: gender || null,
        nationality: nationality || null,
        country_code: countryCode || null,
        employment_type: employmentType,
        hire_date: hireDate,
        work_location: workLocation || null,
        position_id: positionId || null,
        department_id: departmentId || null,
        manager_id: managerId && managerId !== 'none' ? managerId : null,
      }

      const token = localStorage.getItem('access_token')
      console.log('Creating employee with token:', token ? 'Token exists' : 'No token found')
      
      const response = await fetch('http://localhost:8000/api/v1/employees/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(employeeData),
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const error = await response.json()
        console.error('Error response:', error)
        console.error('Full error details:', JSON.stringify(error, null, 2))
        throw new Error(error.detail || error.error?.message || 'Failed to add employee')
      }

      alert('Employee added successfully!')
      
      // Refetch employees so new employee appears in manager dropdown
      await fetchEmployees()
      
      onOpenChange(false)
      resetForm()
      if (onSuccess) onSuccess()
    } catch (error) {
      console.error('Error adding employee:', error)
      alert(`Failed to add employee: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeNumber('')
    setFirstName('')
    setLastName('')
    setWorkEmail('')
    setPhone('')
    setMobile('')
    setDateOfBirth('')
    setGender('')
    setNationality('')
    setCountryCode('')
    setEmploymentType('')
    setWorkLocation('')
    setHireDate('')
    setPositionId('')
    setDepartmentId('')
    setManagerId('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Add New Employee</DialogTitle>
          <DialogDescription>
            Enter the details of the new employee
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Personal Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="employee-number">Employee Number (Auto-generated if empty)</Label>
              <Input
                id="employee-number"
                value={employeeNumber}
                onChange={(e) => setEmployeeNumber(e.target.value)}
                placeholder="Leave empty for auto-generation (EMP-001, EMP-002, etc.)"
              />
              <p className="text-xs text-gray-500">
                Leave blank to auto-generate the next available employee number
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first-name">First Name *</Label>
                <Input
                  id="first-name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="John"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last-name">Last Name *</Label>
                <Input
                  id="last-name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Doe"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dob" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Date of Birth
                </Label>
                <Input
                  id="dob"
                  type="date"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select value={gender} onValueChange={setGender}>
                  <SelectTrigger id="gender">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                    <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nationality">Nationality</Label>
                <Select value={nationality} onValueChange={setNationality}>
                  <SelectTrigger id="nationality">
                    <SelectValue placeholder="Select nationality" />
                  </SelectTrigger>
                  <SelectContent>
                    {countries.length > 0 ? (
                      countries.map((country) => (
                        <SelectItem key={country.country_code} value={country.country_code}>
                          {country.country_name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>No countries configured</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="country-code">Country</Label>
                <Select value={countryCode} onValueChange={setCountryCode}>
                  <SelectTrigger id="country-code">
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent>
                    {countries.length > 0 ? (
                      countries.map((country) => (
                        <SelectItem key={country.country_code} value={country.country_code}>
                          {country.country_code} - {country.country_name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>No countries configured</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contact Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="work-email">Work Email *</Label>
              <Input
                id="work-email"
                type="email"
                value={workEmail}
                onChange={(e) => setWorkEmail(e.target.value)}
                placeholder="john.doe@inara.org"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 234 567 8900"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="mobile">Mobile</Label>
                <Input
                  id="mobile"
                  type="tel"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  placeholder="+1 234 567 8900"
                />
              </div>
            </div>
          </div>

          {/* Employment Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Employment Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="employment-type">Employment Type *</Label>
                <Select value={employmentType} onValueChange={setEmploymentType} required>
                  <SelectTrigger id="employment-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="FULL_TIME">Full Time</SelectItem>
                    <SelectItem value="PART_TIME">Part Time</SelectItem>
                    <SelectItem value="CONTRACT">Contract</SelectItem>
                    <SelectItem value="CONSULTANT">Consultant</SelectItem>
                    <SelectItem value="INTERN">Intern</SelectItem>
                    <SelectItem value="VOLUNTEER">Volunteer</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="hire-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Hire Date *
                </Label>
                <Input
                  id="hire-date"
                  type="date"
                  value={hireDate}
                  onChange={(e) => setHireDate(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="department">Department</Label>
                <Select value={departmentId} onValueChange={setDepartmentId}>
                  <SelectTrigger id="department">
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.length === 0 ? (
                      <SelectItem value="none" disabled>No departments available</SelectItem>
                    ) : (
                      departments.map(dept => (
                        <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Position/Title</Label>
                <Select value={positionId} onValueChange={setPositionId}>
                  <SelectTrigger id="position">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    {positions.length === 0 ? (
                      <SelectItem value="none" disabled>No positions available</SelectItem>
                    ) : (
                      positions.map(pos => (
                        <SelectItem key={pos.id} value={pos.id}>{pos.title}</SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="manager">Manager/Supervisor</Label>
                <Select value={managerId} onValueChange={setManagerId}>
                  <SelectTrigger id="manager">
                    <SelectValue placeholder="Select manager" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Manager</SelectItem>
                    {employees.map(emp => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.first_name} {emp.last_name} ({emp.employee_number})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-gray-500">
                  The person who will approve this employee's leave requests
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="work-location">Work Location</Label>
                <Select value={workLocation} onValueChange={setWorkLocation}>
                  <SelectTrigger id="work-location">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Kabul">Kabul, Afghanistan</SelectItem>
                    <SelectItem value="Beirut">Beirut, Lebanon</SelectItem>
                    <SelectItem value="Cairo">Cairo, Egypt</SelectItem>
                    <SelectItem value="Gaza">Gaza, Palestine</SelectItem>
                    <SelectItem value="Damascus">Damascus, Syria</SelectItem>
                    <SelectItem value="Istanbul">Istanbul, Turkey</SelectItem>
                    <SelectItem value="London">London, United Kingdom</SelectItem>
                  </SelectContent>
                </Select>
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
              {loading ? 'Adding...' : 'Add Employee'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
