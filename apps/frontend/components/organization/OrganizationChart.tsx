'use client'

import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Users, 
  Edit, 
  Plus,
  Building2,
  UserCircle2,
  ChevronDown,
  ChevronUp,
  Mail,
  Phone,
  Download
} from 'lucide-react'

interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  work_email: string
  phone?: string
  position?: {
    id: string
    title: string
  }
  department?: {
    id: string
    name: string
  }
  manager_id?: string
  direct_reports?: Employee[]
  status: string
}

interface Department {
  id: string
  name: string
  code: string
  description?: string
}

export function OrganizationChart() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [selectedManager, setSelectedManager] = useState<string>('')
  const [selectedDepartment, setSelectedDepartment] = useState<string>('')

  useEffect(() => {
    fetchOrganizationData()
  }, [])

  const fetchOrganizationData = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const [employeesRes, departmentsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/employees/organization-chart', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }),
        fetch('http://localhost:8000/api/v1/employees/departments', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
      ])

      if (employeesRes.ok) {
        const empData = await employeesRes.json()
        console.log('Organization chart data:', empData)
        setEmployees(empData)
        // Auto-expand top level
        const topLevel = empData.filter((e: Employee) => !e.manager_id)
        setExpandedNodes(new Set(topLevel.map((e: Employee) => e.id)))
      } else {
        console.error('Failed to fetch employees:', employeesRes.status, await employeesRes.text())
      }

      if (departmentsRes.ok) {
        const deptData = await departmentsRes.json()
        setDepartments(deptData)
      } else {
        console.error('Failed to fetch departments:', departmentsRes.status, await departmentsRes.text())
      }
    } catch (error) {
      console.error('Error fetching organization data:', error)
    } finally {
      setLoading(false)
    }
  }

  const buildHierarchy = (employees: Employee[]): Employee[] => {
    const employeeMap = new Map<string, Employee>()
    
    // Create map of all employees
    employees.forEach(emp => {
      employeeMap.set(emp.id, { ...emp, direct_reports: [] })
    })

    // Build hierarchy
    const roots: Employee[] = []
    employeeMap.forEach(emp => {
      if (emp.manager_id && employeeMap.has(emp.manager_id)) {
        const manager = employeeMap.get(emp.manager_id)!
        if (!manager.direct_reports) manager.direct_reports = []
        manager.direct_reports.push(emp)
      } else {
        roots.push(emp)
      }
    })

    return roots
  }

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const handleEditEmployee = (employee: Employee) => {
    setEditingEmployee(employee)
    setSelectedManager(employee.manager_id || '')
    setSelectedDepartment(employee.department?.id || '')
    setShowEditDialog(true)
  }

  const handleUpdateHierarchy = async () => {
    if (!editingEmployee) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `http://localhost:8000/api/v1/employees/${editingEmployee.id}/hierarchy`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            manager_id: selectedManager || null,
            department_id: selectedDepartment || null,
          }),
        }
      )

      if (response.ok) {
        setShowEditDialog(false)
        fetchOrganizationData()
      } else {
        console.error('Failed to update employee hierarchy')
      }
    } catch (error) {
      console.error('Error updating employee:', error)
    }
  }

  const handleExportPDF = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/employees/organization-chart/export', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `organization_chart_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        console.error('Failed to export PDF:', response.status)
      }
    } catch (error) {
      console.error('Error exporting PDF:', error)
    }
  }

  const renderEmployeeNode = (employee: Employee, level: number = 0) => {
    const hasReports = employee.direct_reports && employee.direct_reports.length > 0
    const isExpanded = expandedNodes.has(employee.id)
    const isTopLevel = level === 0

    return (
      <div key={employee.id} className="flex flex-col items-center">
        {/* Employee Card */}
        <div 
          className={`
            ${isTopLevel 
              ? 'bg-gradient-to-br from-red-50 to-pink-50 border-red-300 shadow-lg' 
              : 'bg-white border-gray-300 shadow-md'
            }
            border-2 rounded-lg p-4 min-w-[180px] max-w-[200px] hover:shadow-xl transition-all cursor-pointer
          `}
          onClick={() => hasReports && toggleNode(employee.id)}
        >
          <div className="flex items-center justify-between mb-3">
            <UserCircle2 className={`w-10 h-10 ${isTopLevel ? 'text-red-600' : 'text-gray-600'}`} />
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                handleEditEmployee(employee)
              }}
              className="h-7 w-7 p-0 hover:bg-gray-200"
            >
              <Edit className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="text-center space-y-2">
            <h3 className={`font-bold text-sm leading-tight ${isTopLevel ? 'text-red-900' : 'text-gray-900'}`}>
              {employee.first_name} {employee.last_name}
            </h3>
            {employee.position && (
              <p className="text-xs font-medium text-gray-700 leading-tight">
                {employee.position.title}
              </p>
            )}
          </div>
        </div>

        {/* Vertical Connector Line */}
        {hasReports && isExpanded && (
          <div className="w-0.5 h-10 bg-gray-400"></div>
        )}

        {/* Direct Reports Container */}
        {hasReports && isExpanded && (
          <div className="flex flex-col items-center">
            {/* Horizontal Line */}
            <div className="relative">
              <div className="h-0.5 bg-gray-400" style={{ width: `${(employee.direct_reports!.length - 1) * 220 + 100}px` }}></div>
              {/* Vertical drops from horizontal line */}
              {employee.direct_reports!.map((_, idx) => (
                <div 
                  key={idx}
                  className="absolute top-0 w-0.5 h-10 bg-gray-400"
                  style={{ left: `${idx * 220 + 50}px` }}
                ></div>
              ))}
            </div>
            
            {/* Direct Reports Grid */}
            <div className="flex gap-10 pt-0">
              {employee.direct_reports!.map(report => (
                <div key={report.id}>
                  {renderEmployeeNode(report, level + 1)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading organization chart...</p>
        </div>
      </div>
    )
  }

  const hierarchy = buildHierarchy(employees)

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader className="bg-gradient-to-r from-pink-600 to-cyan-600 text-white">
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-6 h-6" />
            Organization Chart
          </CardTitle>
          <p className="text-pink-100 text-sm">
            View and manage organizational hierarchy
          </p>
        </CardHeader>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Employees</p>
                <p className="text-3xl font-bold text-gray-900">{employees.length}</p>
              </div>
              <Users className="w-10 h-10 text-pink-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Departments</p>
                <p className="text-3xl font-bold text-gray-900">{departments.length}</p>
              </div>
              <Building2 className="w-10 h-10 text-cyan-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Leadership</p>
                <p className="text-3xl font-bold text-gray-900">{hierarchy.length}</p>
              </div>
              <UserCircle2 className="w-10 h-10 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Organization Hierarchy */}
      <Card className="bg-gradient-to-br from-gray-50 to-gray-100">
        <CardHeader className="text-center pb-6 bg-gradient-to-r from-pink-600 to-cyan-600">
          <div className="flex items-center justify-between">
            <div className="flex-1"></div>
            <div className="flex-1 flex flex-col items-center gap-2">
              <CardTitle className="text-3xl font-bold text-white">
                International Network for Aid, Relief and Assistance
              </CardTitle>
              <p className="text-xl font-light text-white/90">Organogram</p>
            </div>
            <div className="flex-1 flex justify-end">
              <Button
                onClick={handleExportPDF}
                variant="secondary"
                size="sm"
                className="bg-white/20 hover:bg-white/30 text-white border-white/30"
              >
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="overflow-x-auto bg-white">
          {hierarchy.length > 0 ? (
            <div className="flex justify-center items-start gap-20 py-12 min-w-max px-8">
              {hierarchy.map(emp => renderEmployeeNode(emp, 0))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No employees found</p>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Organizational Position</DialogTitle>
            <DialogDescription>
              Update reporting structure and department for {editingEmployee?.first_name} {editingEmployee?.last_name}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Employee Info */}
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="font-semibold">{editingEmployee?.first_name} {editingEmployee?.last_name}</p>
              <p className="text-sm text-gray-600">{editingEmployee?.position?.title}</p>
              <p className="text-sm text-gray-500">{editingEmployee?.work_email}</p>
            </div>

            {/* Manager Selection */}
            <div className="space-y-2">
              <Label htmlFor="manager">Reports To (Manager)</Label>
              <Select value={selectedManager} onValueChange={setSelectedManager}>
                <SelectTrigger id="manager">
                  <SelectValue placeholder="Select manager (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No Manager (Top Level)</SelectItem>
                  {employees
                    .filter(e => e.id !== editingEmployee?.id)
                    .map(emp => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.first_name} {emp.last_name} - {emp.position?.title || 'No title'}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            {/* Department Selection */}
            <div className="space-y-2">
              <Label htmlFor="department">Department</Label>
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger id="department">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map(dept => (
                    <SelectItem key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateHierarchy}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
