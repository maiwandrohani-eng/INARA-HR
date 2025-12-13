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
import { Shield, Plus, Edit, Trash2 } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface Permission {
  id: string
  name: string
  resource: string
  action: string
  description?: string
  created_at: string
}

interface Role {
  id: string
  name: string
  display_name: string
  permissions: Permission[]
}

interface PermissionsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function PermissionsDialog({ open, onOpenChange }: PermissionsDialogProps) {
  const [loading, setLoading] = useState(false)
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [showAddPermission, setShowAddPermission] = useState(false)
  
  // Add permission form
  const [newName, setNewName] = useState('')
  const [newResource, setNewResource] = useState('')
  const [newAction, setNewAction] = useState('')
  const [newDescription, setNewDescription] = useState('')

  useEffect(() => {
    if (open) {
      fetchPermissions()
      fetchRoles()
    }
  }, [open])

  const fetchPermissions = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/auth/permissions', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setPermissions(data)
      }
    } catch (error) {
      console.error('Error fetching permissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoles = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/auth/roles', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setRoles(data)
      }
    } catch (error) {
      console.error('Error fetching roles:', error)
    }
  }

  const handleAddPermission = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      if (!newName || !newResource || !newAction) {
        alert('Please fill in all required fields')
        setLoading(false)
        return
      }

      const permissionData = {
        name: newName,
        resource: newResource,
        action: newAction,
        description: newDescription || null,
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/v1/auth/permissions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(permissionData),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create permission')
      }

      alert('Permission created successfully!')
      setShowAddPermission(false)
      resetAddForm()
      fetchPermissions()
    } catch (error) {
      console.error('Error creating permission:', error)
      alert(`Failed to create permission: ${error instanceof Error ? error.message : 'Please try again'}`)
    } finally {
      setLoading(false)
    }
  }

  const resetAddForm = () => {
    setNewName('')
    setNewResource('')
    setNewAction('')
    setNewDescription('')
  }

  const groupPermissionsByResource = () => {
    const grouped: Record<string, Permission[]> = {}
    permissions.forEach(perm => {
      if (!grouped[perm.resource]) {
        grouped[perm.resource] = []
      }
      grouped[perm.resource].push(perm)
    })
    return grouped
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Permissions Management
          </DialogTitle>
          <DialogDescription>
            Manage system permissions and role assignments
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Add Permission Section */}
          {!showAddPermission ? (
            <div className="flex justify-end">
              <Button onClick={() => setShowAddPermission(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add New Permission
              </Button>
            </div>
          ) : (
            <form onSubmit={handleAddPermission} className="border rounded-lg p-4 space-y-4">
              <h3 className="text-lg font-semibold">Add New Permission</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Permission Name *</Label>
                  <Input
                    id="name"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g., employee:create"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="resource">Resource *</Label>
                  <Input
                    id="resource"
                    value={newResource}
                    onChange={(e) => setNewResource(e.target.value)}
                    placeholder="e.g., employee, leave, user"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="action">Action *</Label>
                  <Select value={newAction} onValueChange={setNewAction} required>
                    <SelectTrigger id="action">
                      <SelectValue placeholder="Select action" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="read">Read</SelectItem>
                      <SelectItem value="write">Write</SelectItem>
                      <SelectItem value="delete">Delete</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="all">All</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Brief description of this permission"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Permission'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowAddPermission(false)
                    resetAddForm()
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {/* Permissions List */}
          <div className="border rounded-lg">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">System Permissions ({permissions.length})</h3>
            </div>
            
            {loading && permissions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Loading permissions...
              </div>
            ) : permissions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No permissions found
              </div>
            ) : (
              <div className="divide-y">
                {Object.entries(groupPermissionsByResource()).map(([resource, perms]) => (
                  <div key={resource} className="p-4">
                    <h4 className="font-semibold text-sm uppercase text-gray-600 mb-2">{resource}</h4>
                    <div className="space-y-2">
                      {perms.map((perm) => (
                        <div key={perm.id} className="flex items-center justify-between pl-4 py-2 hover:bg-gray-50 rounded">
                          <div>
                            <p className="font-medium text-sm">{perm.name}</p>
                            {perm.description && (
                              <p className="text-xs text-gray-500">{perm.description}</p>
                            )}
                          </div>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            perm.action === 'all' ? 'bg-red-100 text-red-800' :
                            perm.action === 'admin' ? 'bg-purple-100 text-purple-800' :
                            perm.action === 'write' ? 'bg-blue-100 text-blue-800' :
                            perm.action === 'delete' ? 'bg-orange-100 text-orange-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {perm.action}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Roles Summary */}
          <div className="border rounded-lg">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">Role Permissions Summary</h3>
            </div>
            <div className="divide-y">
              {roles.map((role) => (
                <div key={role.id} className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{role.display_name}</h4>
                    <span className="text-sm text-gray-500">
                      {role.permissions.length} permission(s)
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.map((perm) => (
                      <span
                        key={perm.id}
                        className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                      >
                        {perm.name}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
