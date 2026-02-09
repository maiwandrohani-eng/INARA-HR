'use client'

import { useState, useEffect } from 'react'
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
import { Textarea } from '@/components/ui/textarea'
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
  
  // Contract & Compensation
  const [salary, setSalary] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [contractType, setContractType] = useState('')
  const [contractStartDate, setContractStartDate] = useState('')
  const [contractEndDate, setContractEndDate] = useState('')
  const [probationEndDate, setProbationEndDate] = useState('')
  
  // Additional Details
  const [nationalId, setNationalId] = useState('')
  const [passportNumber, setPassportNumber] = useState('')
  const [bloodType, setBloodType] = useState('')
  const [medicalConditions, setMedicalConditions] = useState('')
  const [workType, setWorkType] = useState('')
  
  // Emergency Contact 1
  const [emergencyContactName, setEmergencyContactName] = useState('')
  const [emergencyContactPhone, setEmergencyContactPhone] = useState('')
  const [emergencyContactRelationship, setEmergencyContactRelationship] = useState('')
  
  // Emergency Contact 2
  const [emergencyContact2Name, setEmergencyContact2Name] = useState('')
  const [emergencyContact2Phone, setEmergencyContact2Phone] = useState('')
  const [emergencyContact2Relationship, setEmergencyContact2Relationship] = useState('')
  const [emergencyContact2Note, setEmergencyContact2Note] = useState('')

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
      const response = await fetch(`${API_BASE_URL}/employees/`, {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setEmployees(data)
      }
    } catch (error) {
      console.error('Error fetching employees:', error)
    }
  }

  const fetchDepartments = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/employees/departments`, {
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
      const response = await fetch(`${API_BASE_URL}/employees/positions`, {
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
      const response = await fetch(`${API_BASE_URL}/admin/countries`, {
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
        employee_number: employeeNumber || null,
        first_name: firstName,
        last_name: lastName,
        work_email: workEmail,
        phone: phone || null,
        mobile: mobile || null,
        date_of_birth: dateOfBirth || null,
        gender: gender || null,
        nationality: nationality || null,
        national_id: nationalId || null,
        passport_number: passportNumber || null,
        country_code: countryCode || null,
        employment_type: employmentType,
        hire_date: hireDate,
        probation_end_date: probationEndDate || null,
        work_location: workLocation || null,
        position_id: positionId || null,
        department_id: departmentId || null,
        manager_id: managerId && managerId !== 'none' ? managerId : null,
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
        // Contract details (if provided, backend will create contract)
        salary: salary ? parseFloat(salary) : null,
        currency: currency || 'USD',
        contract_type: contractType || null,
        contract_start_date: contractStartDate || null,
        contract_end_date: contractEndDate || null,
      }

      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_BASE_URL}/employees/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(employeeData),
      })
      
      if (!response.ok) {
        const error = await response.json()
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
    setSalary('')
    setCurrency('USD')
    setContractType('')
    setContractStartDate('')
    setContractEndDate('')
    setProbationEndDate('')
    setNationalId('')
    setPassportNumber('')
    setBloodType('')
    setMedicalConditions('')
    setWorkType('')
    setEmergencyContactName('')
    setEmergencyContactPhone('')
    setEmergencyContactRelationship('')
    setEmergencyContact2Name('')
    setEmergencyContact2Phone('')
    setEmergencyContact2Relationship('')
    setEmergencyContact2Note('')
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
                placeholder="Leave empty for auto-generation"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first-name">First Name *</Label>
                <Input
                  id="first-name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last-name">Last Name *</Label>
                <Input
                  id="last-name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dob">Date of Birth</Label>
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
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="national-id">National ID</Label>
                <Input
                  id="national-id"
                  value={nationalId}
                  onChange={(e) => setNationalId(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="passport">Passport Number</Label>
                <Input
                  id="passport"
                  value={passportNumber}
                  onChange={(e) => setPassportNumber(e.target.value)}
                />
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
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="mobile">Mobile</Label>
                <Input
                  id="mobile"
                  type="tel"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Emergency Contacts */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Emergency Contacts</h3>
            
            {/* Emergency Contact 1 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Primary Emergency Contact</h4>
              <div className="grid grid-cols-3 gap-4">
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
                    type="tel"
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

            {/* Emergency Contact 2 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Secondary Emergency Contact</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="emergency-2-name">Contact Name</Label>
                  <Input
                    id="emergency-2-name"
                    value={emergencyContact2Name}
                    onChange={(e) => setEmergencyContact2Name(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="emergency-2-phone">Contact Phone</Label>
                  <Input
                    id="emergency-2-phone"
                    type="tel"
                    value={emergencyContact2Phone}
                    onChange={(e) => setEmergencyContact2Phone(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="emergency-2-relationship">Relationship</Label>
                  <Input
                    id="emergency-2-relationship"
                    value={emergencyContact2Relationship}
                    onChange={(e) => setEmergencyContact2Relationship(e.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="emergency-2-note">Notes</Label>
                <Textarea
                  id="emergency-2-note"
                  className="min-h-[80px]"
                  value={emergencyContact2Note}
                  onChange={(e) => setEmergencyContact2Note(e.target.value)}
                  placeholder="Additional notes about this emergency contact..."
                />
              </div>
            </div>
          </div>

          {/* Medical & Health Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Medical & Health Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="blood-type">Blood Type</Label>
                <Select value={bloodType} onValueChange={setBloodType}>
                  <SelectTrigger id="blood-type">
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
                <Label htmlFor="work-type">Type of Work</Label>
                <Select value={workType} onValueChange={setWorkType}>
                  <SelectTrigger id="work-type">
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

            <div className="space-y-2">
              <Label htmlFor="medical-conditions">Pre-existing Medical Conditions</Label>
              <Textarea
                id="medical-conditions"
                className="min-h-[100px]"
                value={medicalConditions}
                onChange={(e) => setMedicalConditions(e.target.value)}
                placeholder="List any pre-existing medical conditions, allergies, or health concerns..."
              />
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
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="hire-date">Hire Date *</Label>
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
                    {departments.map(dept => (
                      <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Position</Label>
                <Select value={positionId} onValueChange={setPositionId}>
                  <SelectTrigger id="position">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    {positions.map(pos => (
                      <SelectItem key={pos.id} value={pos.id}>{pos.title}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="manager">Line Manager / Supervisor</Label>
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
                  Manager who will approve leave requests, performance appraisals, and review attendance
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="work-country">Work Country</Label>
                <Select value={countryCode} onValueChange={(value) => {
                  setCountryCode(value)
                  setWorkLocation('') // Clear city when country changes
                }}>
                  <SelectTrigger id="work-country">
                    <SelectValue placeholder="Select country" />
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
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="work-location">Work City</Label>
                <Select value={workLocation} onValueChange={setWorkLocation}>
                  <SelectTrigger id="work-location">
                    <SelectValue placeholder="Select city" />
                  </SelectTrigger>
                  <SelectContent>
                    {countryCode === 'AF' && (
                      <>
                        <SelectItem value="Kabul">Kabul</SelectItem>
                        <SelectItem value="Herat">Herat</SelectItem>
                        <SelectItem value="Kandahar">Kandahar</SelectItem>
                        <SelectItem value="Mazar-i-Sharif">Mazar-i-Sharif</SelectItem>
                        <SelectItem value="Jalalabad">Jalalabad</SelectItem>
                      </>
                    )}
                    {countryCode === 'LB' && (
                      <>
                        <SelectItem value="Beirut">Beirut</SelectItem>
                        <SelectItem value="Tripoli">Tripoli</SelectItem>
                        <SelectItem value="Sidon">Sidon</SelectItem>
                        <SelectItem value="Tyre">Tyre</SelectItem>
                      </>
                    )}
                    {countryCode === 'EG' && (
                      <>
                        <SelectItem value="Cairo">Cairo</SelectItem>
                        <SelectItem value="Alexandria">Alexandria</SelectItem>
                        <SelectItem value="Giza">Giza</SelectItem>
                      </>
                    )}
                    {countryCode === 'PS' && (
                      <>
                        <SelectItem value="Gaza">Gaza</SelectItem>
                        <SelectItem value="Ramallah">Ramallah</SelectItem>
                        <SelectItem value="Hebron">Hebron</SelectItem>
                        <SelectItem value="Nablus">Nablus</SelectItem>
                      </>
                    )}
                    {countryCode === 'SY' && (
                      <>
                        <SelectItem value="Damascus">Damascus</SelectItem>
                        <SelectItem value="Aleppo">Aleppo</SelectItem>
                        <SelectItem value="Homs">Homs</SelectItem>
                      </>
                    )}
                    {countryCode === 'TR' && (
                      <>
                        <SelectItem value="Istanbul">Istanbul</SelectItem>
                        <SelectItem value="Ankara">Ankara</SelectItem>
                        <SelectItem value="Izmir">Izmir</SelectItem>
                      </>
                    )}
                    {countryCode === 'GB' && (
                      <>
                        <SelectItem value="London">London</SelectItem>
                        <SelectItem value="Manchester">Manchester</SelectItem>
                        <SelectItem value="Birmingham">Birmingham</SelectItem>
                      </>
                    )}
                    {!countryCode && (
                      <SelectItem value="none" disabled>Please select a country first</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Contract & Compensation */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contract & Compensation</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="salary">Monthly Salary</Label>
                <Input
                  id="salary"
                  type="number"
                  step="0.01"
                  value={salary}
                  onChange={(e) => setSalary(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <Select value={currency} onValueChange={setCurrency}>
                  <SelectTrigger id="currency">
                    <SelectValue placeholder="Currency" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD</SelectItem>
                    <SelectItem value="AFN">AFN</SelectItem>
                    <SelectItem value="EUR">EUR</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="contract-type">Contract Type</Label>
                <Select value={contractType} onValueChange={setContractType}>
                  <SelectTrigger id="contract-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Permanent">Permanent</SelectItem>
                    <SelectItem value="Fixed-Term">Fixed-Term</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contract-start">Contract Start Date</Label>
                <Input
                  id="contract-start"
                  type="date"
                  value={contractStartDate}
                  onChange={(e) => setContractStartDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contract-end">Contract End Date</Label>
                <Input
                  id="contract-end"
                  type="date"
                  value={contractEndDate}
                  onChange={(e) => setContractEndDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="probation-end">Probation End Date</Label>
                <Input
                  id="probation-end"
                  type="date"
                  value={probationEndDate}
                  onChange={(e) => setProbationEndDate(e.target.value)}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Employee'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

