'use client'

import { useState, useMemo, useEffect } from 'react'
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
import { Calendar as CalendarIcon, Plus, Trash2 } from 'lucide-react'
import { useEmployees, getEmployeeFullName } from '@/hooks/useEmployees'

interface ProjectHours {
  [key: string]: { [day: number]: number }
}

interface LeaveHours {
  [key: string]: { [day: number]: number }
}

interface TimesheetFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function TimesheetForm({ open, onOpenChange }: TimesheetFormProps) {
  const [loading, setLoading] = useState(false)
  const { employees, loading: employeesLoading } = useEmployees()
  
  // Employee information
  const [employeeId, setEmployeeId] = useState('')
  const [employeePosition, setEmployeePosition] = useState('')
  const [dutyStation, setDutyStation] = useState('')
  const [lineManager, setLineManager] = useState('')
  const [month, setMonth] = useState('')
  const [year, setYear] = useState('2024')
  
  // Get selected employee details
  const selectedEmployee = employees.find(emp => emp.id === employeeId)
  
  // Auto-populate fields when employee is selected
  useEffect(() => {
    if (selectedEmployee) {
      // Auto-populate employee position/job title
      setEmployeePosition(selectedEmployee.job_title || selectedEmployee.position || '')
      
      // Auto-populate duty station from work location or office location
      setDutyStation(selectedEmployee.work_location || selectedEmployee.office_location || '')
      
      // Auto-populate line manager from reporting manager
      if (selectedEmployee.reporting_manager_id) {
        const manager = employees.find(emp => emp.id === selectedEmployee.reporting_manager_id)
        if (manager) {
          setLineManager(getEmployeeFullName(manager))
        }
      }
    }
  }, [selectedEmployee, employees])
  
  // Projects/Grants
  const [projects, setProjects] = useState<string[]>([''])
  const [projectHours, setProjectHours] = useState<ProjectHours>({})
  
  // Leave types
  const [leaveHours, setLeaveHours] = useState<LeaveHours>({
    'Official Holiday': {},
    'Annual leave': {},
    'Sick leave': {},
    'Unpaid leave': {},
    'Maternity/Paternity leave': {},
    'Bereavement leave': {},
    'Marriage leave': {},
  })
  
  const [comments, setComments] = useState('')

  // Calculate days in selected month
  const daysInMonth = useMemo(() => {
    if (!month || !year) return 31
    const date = new Date(parseInt(year), parseInt(month), 0)
    return date.getDate()
  }, [month, year])

  // Get day of week for a specific date (0 = Sunday, 6 = Saturday)
  const getDayOfWeek = (day: number): number => {
    if (!month || !year) return 0
    return new Date(parseInt(year), parseInt(month) - 1, day).getDay()
  }

  // Get day name abbreviation
  const getDayName = (day: number): string => {
    const dayOfWeek = getDayOfWeek(day)
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days[dayOfWeek]
  }

  // Check if day is weekend
  const isWeekend = (day: number): boolean => {
    const dayOfWeek = getDayOfWeek(day)
    return dayOfWeek === 0 || dayOfWeek === 6 // Sunday or Saturday
  }

  const addProject = () => {
    setProjects([...projects, ''])
  }

  const removeProject = (index: number) => {
    if (projects.length > 1) {
      const newProjects = projects.filter((_, i) => i !== index)
      setProjects(newProjects)
      // Remove hours for deleted project
      const newHours = { ...projectHours }
      delete newHours[projects[index]]
      setProjectHours(newHours)
    }
  }

  const updateProject = (index: number, value: string) => {
    const newProjects = [...projects]
    const oldProject = newProjects[index]
    newProjects[index] = value
    setProjects(newProjects)
    
    // Update hours mapping if project name changed
    if (oldProject && projectHours[oldProject]) {
      const newHours = { ...projectHours }
      newHours[value] = newHours[oldProject]
      delete newHours[oldProject]
      setProjectHours(newHours)
    }
  }

  const updateProjectHours = (project: string, day: number, hours: string) => {
    const hoursValue = parseFloat(hours) || 0
    setProjectHours(prev => ({
      ...prev,
      [project]: {
        ...prev[project],
        [day]: hoursValue
      }
    }))
  }

  const updateLeaveHours = (leaveType: string, day: number, hours: string) => {
    const hoursNum = hours === '' ? 0 : parseFloat(hours)
    setLeaveHours(prev => ({
      ...prev,
      [leaveType]: {
        ...prev[leaveType],
        [day]: hoursNum
      }
    }))
  }

  const calculateDailyTotal = (day: number) => {
    let total = 0
    // Sum all project hours for this day
    projects.forEach(project => {
      if (project && projectHours[project]?.[day]) {
        total += projectHours[project][day]
      }
    })
    // Add leave hours for this day
    total += calculateLeaveTotalForDay(day)
    return total
  }

  const calculateProjectTotal = (project: string) => {
    if (!projectHours[project]) return 0
    return Object.values(projectHours[project]).reduce((sum, hours) => sum + hours, 0)
  }

  const calculateProjectPercentage = (project: string) => {
    const projectTotal = calculateProjectTotal(project)
    const grandTotal = calculateGrandTotal()
    if (grandTotal === 0) return '0.00%'
    return ((projectTotal / grandTotal) * 100).toFixed(2) + '%'
  }

  const calculateGrandTotal = () => {
    let total = 0
    projects.forEach(project => {
      if (project) {
        total += calculateProjectTotal(project)
      }
    })
    // Add all leave hours
    Object.keys(leaveHours).forEach(leaveType => {
      total += calculateLeaveTotal(leaveType)
    })
    return total
  }
  const calculateLeaveTotal = (leaveType: string): number => {
    let total = 0
    const leaveData = leaveHours[leaveType] || {}
    Object.values(leaveData).forEach(hours => {
      total += hours
    })
    return total
  }

  const calculateLeaveTotalForDay = (day: number): number => {
    let total = 0
    Object.keys(leaveHours).forEach(leaveType => {
      total += leaveHours[leaveType]?.[day] || 0
    })
    return total
  }
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Build entries array from grid data
      const entries: any[] = []
      
      projects.forEach(project => {
        if (project && projectHours[project]) {
          Object.entries(projectHours[project]).forEach(([day, hours]) => {
            if (hours > 0) {
              const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
              entries.push({
                project_id: project, // TODO: Map to actual project UUID
                date: date.toISOString().split('T')[0],
                hours: hours,
                activity_description: `Work on ${project}`,
                notes: ''
              })
            }
          })
        }
      })

      const timesheetData = {
        employee_id: employeeId,
        employee_name: selectedEmployee ? getEmployeeFullName(selectedEmployee) : '',
        employee_position: employeePosition,
        duty_station: dutyStation,
        line_manager: lineManager,
        month_year: `${month}/${year}`,
        period_start: `${year}-${month}-01`,
        period_end: `${year}-${month}-${daysInMonth}`,
        total_hours: calculateGrandTotal(),
        status: 'draft',
        entries: entries,
        comments: comments
      }

      const response = await fetch('http://localhost:8000/api/v1/timesheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // TODO: Add auth token
        },
        body: JSON.stringify(timesheetData),
      })

      if (!response.ok) {
        throw new Error('Failed to submit timesheet')
      }

      alert('Timesheet submitted successfully!')
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error submitting timesheet:', error)
      alert('Failed to submit timesheet. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setEmployeeId('')
    setEmployeePosition('')
    setDutyStation('')
    setLineManager('')
    setMonth('')
    setYear('2024')
    setProjects([''])
    setProjectHours({})
    setLeaveHours({
      'Official Holiday': {},
      'Annual leave': {},
      'Sick leave': {},
      'Unpaid leave': {},
      'Maternity/Paternity leave': {},
      'Bereavement leave': {},
      'Marriage leave': {},
    })
    setComments('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
            Monthly Timesheet
          </DialogTitle>
          <DialogDescription>
            Enter your daily work hours by project for the month. Use 8.00 hours for a standard work day.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Employee Information Header */}
          <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
            <div className="space-y-2">
              <Label htmlFor="employee-name">Employee Name</Label>
              <Select value={employeeId} onValueChange={setEmployeeId} required>
                <SelectTrigger id="employee-name">
                  <SelectValue placeholder={employeesLoading ? "Loading employees..." : "Select employee"} />
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
              <Label htmlFor="position">Employee Position</Label>
              <Input
                id="position"
                value={selectedEmployee?.work_location || dutyStation}
                onChange={(e) => setDutyStation(e.target.value)}
                placeholder="Position/Role"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="duty-station">Duty Station</Label>
              <Input
                id="duty-station"
                value={dutyStation}
                onChange={(e) => setDutyStation(e.target.value)}
                placeholder="Gaza"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="line-manager">Line Manager</Label>
              <Input
                id="line-manager"
                value={lineManager}
                onChange={(e) => setLineManager(e.target.value)}
                placeholder="Sara"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="month" className="flex items-center gap-2">
                <CalendarIcon className="h-4 w-4" />
                Month
              </Label>
              <Select value={month} onValueChange={setMonth} required>
                <SelectTrigger id="month">
                  <SelectValue placeholder="Select month" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">January</SelectItem>
                  <SelectItem value="2">February</SelectItem>
                  <SelectItem value="3">March</SelectItem>
                  <SelectItem value="4">April</SelectItem>
                  <SelectItem value="5">May</SelectItem>
                  <SelectItem value="6">June</SelectItem>
                  <SelectItem value="7">July</SelectItem>
                  <SelectItem value="8">August</SelectItem>
                  <SelectItem value="9">September</SelectItem>
                  <SelectItem value="10">October</SelectItem>
                  <SelectItem value="11">November</SelectItem>
                  <SelectItem value="12">December</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="year" className="flex items-center gap-2">
                <CalendarIcon className="h-4 w-4" />
                Year
              </Label>
              <Select value={year} onValueChange={setYear} required>
                <SelectTrigger id="year">
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2023">2023</SelectItem>
                  <SelectItem value="2024">2024</SelectItem>
                  <SelectItem value="2025">2025</SelectItem>
                  <SelectItem value="2026">2026</SelectItem>
                  <SelectItem value="2027">2027</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Timesheet Grid */}
          <div className="overflow-x-auto border rounded-lg">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="bg-blue-200 border-b">
                  <th className="border p-2 text-left font-semibold min-w-[150px]">
                    Project \ Grant Name
                  </th>
                  {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => (
                    <th key={day} className={`border p-1 text-center font-semibold w-8 ${
                      isWeekend(day) ? 'bg-gray-300' : ''
                    }`}>
                      <div className="text-[10px] leading-tight">{getDayName(day)}</div>
                      <div className="font-bold">{day}</div>
                    </th>
                  ))}
                  <th className="border p-2 text-center font-semibold bg-blue-300">TOTALS</th>
                  <th className="border p-2 text-center font-semibold bg-blue-300">% of Time</th>
                </tr>
              </thead>
              <tbody>
                {/* Project Rows */}
                {projects.map((project, projectIndex) => (
                  <tr key={projectIndex} className="hover:bg-gray-50">
                    <td className="border p-1">
                      <div className="flex gap-1">
                        <Input
                          value={project}
                          onChange={(e) => updateProject(projectIndex, e.target.value)}
                          placeholder="Enter project/grant name"
                          className="h-7 text-xs"
                        />
                        {projects.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeProject(projectIndex)}
                            className="h-7 w-7 p-0 text-red-600"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </td>
                    {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => (
                      <td key={day} className={`border p-0 ${
                        isWeekend(day) ? 'bg-gray-100' : ''
                      }`}>
                        <Input
                          type="number"
                          step="0.25"
                          min="0"
                          max="24"
                          value={projectHours[project]?.[day] || ''}
                          onChange={(e) => updateProjectHours(project, day, e.target.value)}
                          className={`h-7 text-xs text-center border-0 rounded-none p-0 ${
                            isWeekend(day) ? 'bg-gray-100' : ''
                          }`}
                          placeholder=""
                        />
                      </td>
                    ))}
                    <td className="border p-2 text-center font-semibold bg-gray-100">
                      {project ? calculateProjectTotal(project).toFixed(2) : '0.00'}
                    </td>
                    <td className="border p-2 text-center bg-gray-100">
                      {project ? calculateProjectPercentage(project) : '0.00%'}
                    </td>
                  </tr>
                ))}
                
                {/* Add Project Button Row */}
                <tr>
                  <td colSpan={daysInMonth + 3} className="border p-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={addProject}
                      className="w-full"
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      Add Project/Grant
                    </Button>
                  </td>
                </tr>

                {/* Spacer Row */}
                <tr>
                  <td colSpan={daysInMonth + 3} className="border-0 h-2"></td>
                </tr>

                {/* Leave Types Section */}
                {Object.keys(leaveHours).map((leaveType) => (
                  <tr key={leaveType} className="hover:bg-gray-50 bg-yellow-50">
                    <td className="border p-2 font-medium">{leaveType}</td>
                    {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => (
                      <td key={day} className={`border p-0 ${
                        isWeekend(day) ? 'bg-gray-200' : ''
                      }`}>
                        <Input
                          type="number"
                          step="0.25"
                          min="0"
                          max="24"
                          value={leaveHours[leaveType]?.[day] || ''}
                          onChange={(e) => updateLeaveHours(leaveType, day, e.target.value)}
                          className={`h-7 text-xs text-center border-0 rounded-none p-0 ${
                            isWeekend(day) ? 'bg-gray-200' : ''
                          }`}
                          placeholder=""
                        />
                      </td>
                    ))}
                    <td className="border p-2 text-center font-semibold bg-yellow-100">
                      {calculateLeaveTotal(leaveType).toFixed(2)}
                    </td>
                    <td className="border p-2 text-center bg-yellow-100">
                      {calculateGrandTotal() > 0 ? ((calculateLeaveTotal(leaveType) / calculateGrandTotal()) * 100).toFixed(2) : '0.00'}%
                    </td>
                  </tr>
                ))}

                {/* Comments Row */}
                <tr>
                  <td colSpan={daysInMonth + 3} className="border p-2">
                    <Label className="text-xs font-semibold">Comments:</Label>
                    <Textarea
                      value={comments}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setComments(e.target.value)}
                      className="mt-1 text-xs"
                      rows={2}
                      placeholder="Enter any comments or notes..."
                    />
                  </td>
                </tr>

                {/* Totals Row */}
                <tr className="bg-blue-200 font-bold">
                  <td className="border p-2">TOTALS:</td>
                  {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
                    const total = calculateDailyTotal(day)
                    return (
                      <td key={day} className={`border p-2 text-center ${
                        isWeekend(day) ? 'bg-gray-300' : ''
                      }`}>
                        {total > 0 ? total.toFixed(2) : '-'}
                      </td>
                    )
                  })}
                  <td className="border p-2 text-center bg-blue-300">{calculateGrandTotal().toFixed(2)}</td>
                  <td className="border p-2 text-center bg-blue-300">100.00%</td>
                </tr>
              </tbody>
            </table>
          </div>

          <DialogFooter className="gap-2 pt-4">
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
              {loading ? 'Submitting...' : 'Submit Timesheet'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
