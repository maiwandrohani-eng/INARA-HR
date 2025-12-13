/**
 * Departments & Positions Management Dialog
 * Allows admins to create and manage departments and positions
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Building2, Briefcase, Trash2, Edit2, X } from 'lucide-react'

interface Department {
  id: string
  name: string
  code: string
  description?: string
}

interface Position {
  id: string
  title: string
  code: string
  level?: string
  description?: string
}

interface DepartmentsPositionsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function DepartmentsPositionsDialog({ open, onOpenChange }: DepartmentsPositionsDialogProps) {
  const [departments, setDepartments] = useState<Department[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(false)

  // Edit mode
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [editingPos, setEditingPos] = useState<Position | null>(null)

  // Department form
  const [deptName, setDeptName] = useState('')
  const [deptCode, setDeptCode] = useState('')
  const [deptDescription, setDeptDescription] = useState('')

  // Position form
  const [posTitle, setPosTitle] = useState('')
  const [posCode, setPosCode] = useState('')
  const [posLevel, setPosLevel] = useState('')
  const [posDescription, setPosDescription] = useState('')

  useEffect(() => {
    if (open) {
      fetchDepartments()
      fetchPositions()
    }
  }, [open])

  const fetchDepartments = async () => {
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      console.log('Fetching departments with token:', token ? 'Token exists' : 'No token')
      const response = await fetch('http://localhost:8000/api/v1/employees/departments', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      console.log('Departments response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('Departments fetched:', data)
        setDepartments(data)
      } else {
        const error = await response.text()
        console.error('Failed to fetch departments:', response.status, error)
      }
    } catch (error) {
      console.error('Error fetching departments:', error)
    }
  }

  const fetchPositions = async () => {
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      console.log('Fetching positions with token:', token ? 'Token exists' : 'No token')
      const response = await fetch('http://localhost:8000/api/v1/employees/positions', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
      console.log('Positions response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('Positions fetched:', data)
        setPositions(data)
      } else {
        const error = await response.text()
        console.error('Failed to fetch positions:', response.status, error)
      }
    } catch (error) {
      console.error('Error fetching positions:', error)
    }
  }

  const handleAddDepartment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!deptName || !deptCode) {
      alert('Please fill in department name and code')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const url = editingDept 
        ? `http://localhost:8000/api/v1/employees/departments/${editingDept.id}`
        : 'http://localhost:8000/api/v1/employees/departments'
      
      const method = editingDept ? 'PUT' : 'POST'
      
      console.log(`${method}ing department:`, { name: deptName, code: deptCode, description: deptDescription })
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: deptName,
          code: deptCode,
          description: deptDescription || null,
          country_code: 'US',
        }),
      })

      console.log('Department response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Department operation failed:', response.status, errorText)
        let errorMessage = `Failed to ${editingDept ? 'update' : 'create'} department`
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const result = await response.json()
      console.log('Department operation successful:', result)

      setDeptName('')
      setDeptCode('')
      setDeptDescription('')
      setEditingDept(null)
      await fetchDepartments()
      alert(`Department ${editingDept ? 'updated' : 'created'} successfully!`)
    } catch (error) {
      console.error('Error with department:', error)
      alert(`Failed to ${editingDept ? 'update' : 'create'} department: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEditDepartment = (dept: Department) => {
    setEditingDept(dept)
    setDeptName(dept.name)
    setDeptCode(dept.code)
    setDeptDescription(dept.description || '')
  }

  const handleCancelEditDepartment = () => {
    setEditingDept(null)
    setDeptName('')
    setDeptCode('')
    setDeptDescription('')
  }

  const handleDeleteDepartment = async (deptId: string) => {
    if (!confirm('Are you sure you want to delete this department?')) {
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      const response = await fetch(`http://localhost:8000/api/v1/employees/departments/${deptId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        let errorMessage = 'Failed to delete department'
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      await fetchDepartments()
      alert('Department deleted successfully!')
    } catch (error) {
      console.error('Error deleting department:', error)
      alert(`Failed to delete department: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleAddPosition = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!posTitle || !posCode) {
      alert('Please fill in position title and code')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      if (!token) {
        throw new Error('No authentication token found. Please log in again.')
      }

      const url = editingPos
        ? `http://localhost:8000/api/v1/employees/positions/${editingPos.id}`
        : 'http://localhost:8000/api/v1/employees/positions'
      
      const method = editingPos ? 'PUT' : 'POST'
      
      console.log(`${method}ing position:`, { title: posTitle, code: posCode, level: posLevel, description: posDescription })
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: posTitle,
          code: posCode,
          level: posLevel || null,
          description: posDescription || null,
          country_code: 'US',
        }),
      })

      console.log('Position response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Position operation failed:', response.status, errorText)
        let errorMessage = `Failed to ${editingPos ? 'update' : 'create'} position`
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const result = await response.json()
      console.log('Position operation successful:', result)

      setPosTitle('')
      setPosCode('')
      setPosLevel('')
      setPosDescription('')
      setEditingPos(null)
      await fetchPositions()
      alert(`Position ${editingPos ? 'updated' : 'created'} successfully!`)
    } catch (error) {
      console.error('Error with position:', error)
      alert(`Failed to ${editingPos ? 'update' : 'create'} position: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleEditPosition = (pos: Position) => {
    setEditingPos(pos)
    setPosTitle(pos.title)
    setPosCode(pos.code)
    setPosLevel(pos.level || '')
    setPosDescription(pos.description || '')
  }

  const handleCancelEditPosition = () => {
    setEditingPos(null)
    setPosTitle('')
    setPosCode('')
    setPosLevel('')
    setPosDescription('')
  }

  const handleDeletePosition = async (posId: string) => {
    if (!confirm('Are you sure you want to delete this position?')) {
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      const response = await fetch(`http://localhost:8000/api/v1/employees/positions/${posId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const errorText = await response.text()
        let errorMessage = 'Failed to delete position'
        try {
          const errorJson = JSON.parse(errorText)
          errorMessage = errorJson.detail || errorMessage
        } catch {
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      await fetchPositions()
      alert('Position deleted successfully!')
    } catch (error) {
      console.error('Error deleting position:', error)
      alert(`Failed to delete position: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Departments & Positions</DialogTitle>
          <DialogDescription>
            Manage organizational departments and job positions
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="departments" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="departments">
              <Building2 className="w-4 h-4 mr-2" />
              Departments
            </TabsTrigger>
            <TabsTrigger value="positions">
              <Briefcase className="w-4 h-4 mr-2" />
              Positions
            </TabsTrigger>
          </TabsList>

          {/* DEPARTMENTS TAB */}
          <TabsContent value="departments" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  {editingDept ? 'Edit Department' : 'Add New Department'}
                  {editingDept && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={handleCancelEditDepartment}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Cancel
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddDepartment} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="dept-name">Department Name *</Label>
                      <Input
                        id="dept-name"
                        value={deptName}
                        onChange={(e) => setDeptName(e.target.value)}
                        placeholder="e.g., Human Resources"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dept-code">Department Code *</Label>
                      <Input
                        id="dept-code"
                        value={deptCode}
                        onChange={(e) => setDeptCode(e.target.value)}
                        placeholder="e.g., HR"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dept-desc">Description</Label>
                    <Input
                      id="dept-desc"
                      value={deptDescription}
                      onChange={(e) => setDeptDescription(e.target.value)}
                      placeholder="Optional description"
                    />
                  </div>
                  <Button type="submit" disabled={loading}>
                    {editingDept ? (
                      <>
                        <Edit2 className="w-4 h-4 mr-2" />
                        {loading ? 'Updating...' : 'Update Department'}
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        {loading ? 'Adding...' : 'Add Department'}
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Existing Departments ({departments.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {departments.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No departments yet. Add your first department above.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {departments.map((dept) => (
                      <div
                        key={dept.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                      >
                        <div>
                          <p className="font-semibold">{dept.name}</p>
                          <p className="text-sm text-gray-500">Code: {dept.code}</p>
                          {dept.description && (
                            <p className="text-xs text-gray-400 mt-1">{dept.description}</p>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditDepartment(dept)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteDepartment(dept.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* POSITIONS TAB */}
          <TabsContent value="positions" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  {editingPos ? 'Edit Position' : 'Add New Position'}
                  {editingPos && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={handleCancelEditPosition}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Cancel
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddPosition} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="pos-title">Position Title *</Label>
                      <Input
                        id="pos-title"
                        value={posTitle}
                        onChange={(e) => setPosTitle(e.target.value)}
                        placeholder="e.g., HR Manager"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="pos-code">Position Code *</Label>
                      <Input
                        id="pos-code"
                        value={posCode}
                        onChange={(e) => setPosCode(e.target.value)}
                        placeholder="e.g., HRM"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="pos-level">Level</Label>
                      <Input
                        id="pos-level"
                        value={posLevel}
                        onChange={(e) => setPosLevel(e.target.value)}
                        placeholder="e.g., Senior, Manager, Director"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="pos-desc">Description</Label>
                      <Input
                        id="pos-desc"
                        value={posDescription}
                        onChange={(e) => setPosDescription(e.target.value)}
                        placeholder="Optional description"
                      />
                    </div>
                  </div>
                  <Button type="submit" disabled={loading}>
                    {editingPos ? (
                      <>
                        <Edit2 className="w-4 h-4 mr-2" />
                        {loading ? 'Updating...' : 'Update Position'}
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        {loading ? 'Adding...' : 'Add Position'}
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Existing Positions ({positions.length})</CardTitle>
              </CardHeader>
              <CardContent>
                {positions.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    No positions yet. Add your first position above.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {positions.map((pos) => (
                      <div
                        key={pos.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                      >
                        <div>
                          <p className="font-semibold">{pos.title}</p>
                          <p className="text-sm text-gray-500">
                            Code: {pos.code}
                            {pos.level && ` • Level: ${pos.level}`}
                          </p>
                          {pos.description && (
                            <p className="text-xs text-gray-400 mt-1">{pos.description}</p>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditPosition(pos)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeletePosition(pos.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
