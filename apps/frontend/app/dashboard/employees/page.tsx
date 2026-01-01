'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Search, Filter, Download, Eye, Edit, Upload, FileUp, Trash2, UserCheck, UserX } from 'lucide-react'
import { useEmployees, Employee } from '@/hooks/useEmployees'
import { AddEmployeeForm } from '@/components/forms/AddEmployeeForm'
import { ImportEmployeesDialog } from '@/components/forms/ImportEmployeesDialog'
import { exportEmployeeTemplate, exportToExcel, ExcelColumn } from '@/utils/excelExport'
import { useRouter } from 'next/navigation'

export default function EmployeesPage() {
  const router = useRouter()
  const { employees, loading, refetch } = useEmployees()
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [showFilterDialog, setShowFilterDialog] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [employmentTypeFilter, setEmploymentTypeFilter] = useState('')

  const handleAddEmployee = () => {
    setShowAddForm(true)
  }

  const handleAddSuccess = () => {
    refetch()
  }

  const handleView = (employee: Employee) => {
    router.push(`/dashboard/employees/${employee.id}`)
  }

  const handleEdit = (employee: Employee) => {
    router.push(`/dashboard/employees/${employee.id}/edit`)
  }

  const handleDelete = async (employee: Employee) => {
    if (!confirm(`Are you sure you want to delete ${employee.first_name} ${employee.last_name}?`)) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/employees/${employee.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Employee deleted successfully')
        refetch()
      } else {
        const error = await response.text()
        alert(`Failed to delete employee: ${error}`)
      }
    } catch (error) {
      console.error('Error deleting employee:', error)
      alert('Failed to delete employee')
    }
  }

  const handleActivate = async (employee: Employee) => {
    if (!confirm(`Activate ${employee.first_name} ${employee.last_name}?`)) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/employees/${employee.id}/activate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Employee activated successfully')
        refetch()
      } else {
        const error = await response.text()
        alert(`Failed to activate employee: ${error}`)
      }
    } catch (error) {
      console.error('Error activating employee:', error)
      alert('Failed to activate employee')
    }
  }

  const handleDeactivate = async (employee: Employee) => {
    if (!confirm(`Deactivate ${employee.first_name} ${employee.last_name}? They will no longer have access to the system.`)) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/employees/${employee.id}/deactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        alert('Employee deactivated successfully')
        refetch()
      } else {
        const error = await response.text()
        alert(`Failed to deactivate employee: ${error}`)
      }
    } catch (error) {
      console.error('Error deactivating employee:', error)
      alert('Failed to deactivate employee')
    }
  }

  const handleFilter = () => {
    setShowFilterDialog(!showFilterDialog)
  }

  const clearFilters = () => {
    setStatusFilter('')
    setEmploymentTypeFilter('')
  }

  const handleExportTemplate = () => {
    exportEmployeeTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to add employees in bulk.')
  }

  const handleImport = () => {
    setShowImportDialog(true)
  }

  const handleImportSuccess = () => {
    refetch()
  }

  const handleExportData = () => {
    const columns: ExcelColumn[] = [
      { header: 'Employee Number', key: 'employee_number' },
      { header: 'First Name', key: 'first_name' },
      { header: 'Last Name', key: 'last_name' },
      { header: 'Work Email', key: 'work_email' },
      { header: 'Phone', key: 'phone' },
      { header: 'Mobile', key: 'mobile' },
      { header: 'Work Location', key: 'work_location' },
      { header: 'Employment Type', key: 'employment_type' },
      { header: 'Status', key: 'status' },
    ]
    exportToExcel(employees, columns, 'employees_data')
  }

  const filteredEmployees = employees.filter(emp => {
    const searchLower = searchTerm.toLowerCase()
    const matchesSearch = (
      emp.first_name?.toLowerCase().includes(searchLower) ||
      emp.last_name?.toLowerCase().includes(searchLower) ||
      emp.work_email?.toLowerCase().includes(searchLower) ||
      emp.employee_number?.toLowerCase().includes(searchLower)
    )
    const matchesStatus = !statusFilter || emp.status === statusFilter
    const matchesEmploymentType = !employmentTypeFilter || emp.employment_type === employmentTypeFilter
    
    return matchesSearch && matchesStatus && matchesEmploymentType
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Employees</h1>
          <p className="text-gray-500 mt-2">Manage employee records and information</p>
        </div>
        <Button onClick={handleAddEmployee}>
          <Plus className="w-4 h-4 mr-2" />
          Add Employee
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Employee Directory</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleFilter}>
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm" onClick={handleExportData}>
                <Download className="w-4 h-4 mr-2" />
                Export Data
              </Button>
              <Button variant="outline" size="sm" onClick={handleExportTemplate} className="bg-green-50 hover:bg-green-100">
                <Upload className="w-4 h-4 mr-2" />
                Export Template
              </Button>
              <Button variant="outline" size="sm" onClick={handleImport} className="bg-blue-50 hover:bg-blue-100">
                <FileUp className="w-4 h-4 mr-2" />
                Import Excel
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search employees by name, email, or department..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="border rounded-lg">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      Loading employees...
                    </td>
                  </tr>
                ) : filteredEmployees.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      {searchTerm ? 'No employees found matching your search.' : 'No employees found.'}
                    </td>
                  </tr>
                ) : (
                  filteredEmployees.map((employee) => (
                    <tr key={employee.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">{employee.employee_number}</td>
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-gray-900">
                          {employee.first_name} {employee.last_name}
                        </div>
                        {employee.phone && (
                          <div className="text-xs text-gray-500">{employee.phone}</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">{employee.work_email}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{employee.work_location || '-'}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {employee.employment_type?.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {employee.status?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm" title="View" onClick={() => handleView(employee)}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" title="Edit" onClick={() => handleEdit(employee)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          {employee.status?.toLowerCase() === 'active' ? (
                            <Button variant="ghost" size="sm" title="Deactivate" onClick={() => handleDeactivate(employee)} className="text-orange-600 hover:text-orange-700 hover:bg-orange-50">
                              <UserX className="w-4 h-4" />
                            </Button>
                          ) : (
                            <Button variant="ghost" size="sm" title="Activate" onClick={() => handleActivate(employee)} className="text-green-600 hover:text-green-700 hover:bg-green-50">
                              <UserCheck className="w-4 h-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" title="Delete" onClick={() => handleDelete(employee)} className="text-red-600 hover:text-red-700 hover:bg-red-50">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <AddEmployeeForm 
        open={showAddForm} 
        onOpenChange={setShowAddForm}
        onSuccess={handleAddSuccess}
      />

      <ImportEmployeesDialog
        open={showImportDialog}
        onOpenChange={setShowImportDialog}
        onSuccess={handleImportSuccess}
      />

      {/* Filter Dialog */}
      {showFilterDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Filter Employees</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Status</label>
                <select
                  className="w-full border rounded px-3 py-2"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="terminated">Terminated</option>
                  <option value="on_leave">On Leave</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Employment Type</label>
                <select
                  className="w-full border rounded px-3 py-2"
                  value={employmentTypeFilter}
                  onChange={(e) => setEmploymentTypeFilter(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="full_time">Full Time</option>
                  <option value="part_time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="consultant">Consultant</option>
                  <option value="intern">Intern</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={clearFilters}>
                Clear
              </Button>
              <Button variant="outline" onClick={() => setShowFilterDialog(false)}>
                Close
              </Button>
              <Button onClick={() => setShowFilterDialog(false)}>
                Apply
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
