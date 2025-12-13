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
import apiClient, { api } from '@/lib/api-client'
import { Users, Shield, Trash2, Plus, Edit, Key } from 'lucide-react'

interface Role {
  id: string
  name: string
  display_name: string
}

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  country_code: string
  is_active: boolean
  is_verified: boolean
  roles: Role[]
}

interface UserManagementDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function UserManagementDialog({ open, onOpenChange }: UserManagementDialogProps) {
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [showAddUser, setShowAddUser] = useState(false)
  const [roles, setRoles] = useState<any[]>([])
  
  // Add user form
  const [newEmail, setNewEmail] = useState('')
  const [newFirstName, setNewFirstName] = useState('')
  const [newLastName, setNewLastName] = useState('')
  const [newPhone, setNewPhone] = useState('')
  const [newCountryCode, setNewCountryCode] = useState('')
  const [newRoleId, setNewRoleId] = useState('')
  const [newPassword, setNewPassword] = useState('')

  // Edit user state
  const [showEditUser, setShowEditUser] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [editEmail, setEditEmail] = useState('')
  const [editFirstName, setEditFirstName] = useState('')
  const [editLastName, setEditLastName] = useState('')
  const [editPhone, setEditPhone] = useState('')
  const [editCountryCode, setEditCountryCode] = useState('')
  const [editRoleId, setEditRoleId] = useState('')

  // Password reset state
  const [showPasswordReset, setShowPasswordReset] = useState(false)
  const [resetPasswordUserId, setResetPasswordUserId] = useState('')
  const [resetPasswordUserName, setResetPasswordUserName] = useState('')
  const [newPasswordReset, setNewPasswordReset] = useState('')
  const [confirmPasswordReset, setConfirmPasswordReset] = useState('')

  useEffect(() => {
    if (open) {
      fetchUsers()
      fetchRoles()
    }
  }, [open])

  const fetchRoles = async () => {
    try {
      const data = await api.get('/auth/roles')
      setRoles(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching roles:', error)
      setRoles([])
    }
  }

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const data = await api.get('/auth/users')
      setUsers(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching users:', error)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Validate required fields
      if (!newEmail || !newFirstName || !newLastName || !newPassword || !newCountryCode || !newRoleId) {
        alert('Please fill in all required fields')
        setLoading(false)
        return
      }

      const userData = {
        email: newEmail,
        first_name: newFirstName,
        last_name: newLastName,
        phone: newPhone || null,
        country_code: newCountryCode,
        password: newPassword,
        role_ids: [newRoleId],
      }

      await api.post('/auth/register', userData)

      alert('User created successfully!')
      setShowAddUser(false)
      resetAddForm()
      fetchUsers()
    } catch (error: any) {
      console.error('Error creating user:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Please try again'
      alert(`Failed to create user: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      await api.patch(`/auth/users/${userId}`, { is_active: !isActive })
      fetchUsers()
    } catch (error: any) {
      console.error('Error updating user:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Please try again'
      alert(`Failed to update user status: ${errorMessage}`)
    }
  }

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return

    try {
      await api.delete(`/auth/users/${userId}`)
      alert('User deleted successfully')
      fetchUsers()
    } catch (error: any) {
      console.error('Error deleting user:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Please try again'
      alert(`Failed to delete user: ${errorMessage}`)
    }
  }

  const resetAddForm = () => {
    setNewEmail('')
    setNewFirstName('')
    setNewLastName('')
    setNewPhone('')
    setNewCountryCode('')
    setNewRoleId('')
    setNewPassword('')
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setEditEmail(user.email)
    setEditFirstName(user.first_name)
    setEditLastName(user.last_name)
    setEditPhone(user.phone || '')
    setEditCountryCode(user.country_code)
    setEditRoleId(user.roles && user.roles.length > 0 ? user.roles[0].id : '')
    setShowEditUser(true)
  }

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return

    setLoading(true)
    try {
      const updateData: any = {
        first_name: editFirstName,
        last_name: editLastName,
        phone: editPhone || null,
        country_code: editCountryCode,
      }

      // Update role if changed
      if (editRoleId && (!editingUser.roles || editingUser.roles.length === 0 || editingUser.roles[0].id !== editRoleId)) {
        updateData.role_ids = [editRoleId]
      }

      await api.patch(`/auth/users/${editingUser.id}`, updateData)

      alert('User updated successfully!')
      setShowEditUser(false)
      setEditingUser(null)
      fetchUsers()
    } catch (error: any) {
      console.error('Error updating user:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Please try again'
      alert(`Failed to update user: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenPasswordReset = (user: User) => {
    setResetPasswordUserId(user.id)
    setResetPasswordUserName(`${user.first_name} ${user.last_name}`)
    setNewPasswordReset('')
    setConfirmPasswordReset('')
    setShowPasswordReset(true)
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()

    if (newPasswordReset !== confirmPasswordReset) {
      alert('Passwords do not match')
      return
    }

    if (newPasswordReset.length < 8) {
      alert('Password must be at least 8 characters')
      return
    }

    setLoading(true)
    try {
      await api.patch(`/auth/users/${resetPasswordUserId}/password`, {
        new_password: newPasswordReset
      })

      alert('Password reset successfully!')
      setShowPasswordReset(false)
      setResetPasswordUserId('')
      setResetPasswordUserName('')
      setNewPasswordReset('')
      setConfirmPasswordReset('')
    } catch (error: any) {
      console.error('Error resetting password:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || 'Please try again'
      alert(`Failed to reset password: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            User Management
          </DialogTitle>
          <DialogDescription>
            Manage system users, roles, and permissions
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Add User Section */}
          {!showAddUser ? (
            <div className="flex justify-end">
              <Button onClick={() => setShowAddUser(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add New User
              </Button>
            </div>
          ) : (
            <form onSubmit={handleAddUser} className="border rounded-lg p-4 space-y-4">
              <h3 className="text-lg font-semibold">Add New User</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    placeholder="+1 234 567 8900"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="first-name">First Name *</Label>
                  <Input
                    id="first-name"
                    value={newFirstName}
                    onChange={(e) => setNewFirstName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="last-name">Last Name *</Label>
                  <Input
                    id="last-name"
                    value={newLastName}
                    onChange={(e) => setNewLastName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country-code">Country *</Label>
                  <Select value={newCountryCode} onValueChange={setNewCountryCode} required>
                    <SelectTrigger id="country-code">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="AF">Afghanistan</SelectItem>
                      <SelectItem value="LB">Lebanon</SelectItem>
                      <SelectItem value="EG">Egypt</SelectItem>
                      <SelectItem value="PS">Palestine</SelectItem>
                      <SelectItem value="SY">Syria</SelectItem>
                      <SelectItem value="TR">Turkey</SelectItem>
                      <SelectItem value="GB">United Kingdom</SelectItem>
                      <SelectItem value="JO">Jordan</SelectItem>
                      <SelectItem value="IQ">Iraq</SelectItem>
                      <SelectItem value="YE">Yemen</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="role">Role *</Label>
                  <Select value={newRoleId} onValueChange={setNewRoleId} required>
                    <SelectTrigger id="role">
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      {roles.map((role) => (
                        <SelectItem key={role.id} value={role.id}>
                          {role.display_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min 8 characters, include uppercase, lowercase, and digit"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create User'}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowAddUser(false)
                    resetAddForm()
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}

          {/* Users List */}
          <div className="border rounded-lg">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-semibold">System Users ({users.length})</h3>
            </div>
            
            {loading && users.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Loading users...
              </div>
            ) : users.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No users found
              </div>
            ) : (
              <div className="divide-y">
                {users.map((user) => (
                  <div key={user.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div>
                          <p className="font-semibold">{user.first_name} {user.last_name}</p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                        {user.roles && user.roles.length > 0 && (
                          <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold rounded-full ${
                            user.roles[0].name === 'admin' ? 'bg-red-100 text-red-800' :
                            user.roles[0].name === 'hr_admin' ? 'bg-purple-100 text-purple-800' :
                            user.roles[0].name === 'hr_manager' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            <Shield className="w-3 h-3" />
                            {user.roles[0].display_name}
                          </span>
                        )}
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditUser(user)}
                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleOpenPasswordReset(user)}
                        className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                      >
                        <Key className="w-4 h-4 mr-1" />
                        Reset Password
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleActive(user.id, user.is_active)}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Edit User Dialog */}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    {/* Edit User Dialog */}
    <Dialog open={showEditUser} onOpenChange={(open) => {
      setShowEditUser(open)
      if (!open) {
        setEditingUser(null)
        fetchUsers()
      }
    }}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit User: {editingUser?.email}</DialogTitle>
        </DialogHeader>
        
        {editingUser && (
          <form onSubmit={handleUpdateUser} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="edit-first-name">First Name *</Label>
                      <Input
                        id="edit-first-name"
                        value={editFirstName}
                        onChange={(e) => setEditFirstName(e.target.value)}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-last-name">Last Name *</Label>
                      <Input
                        id="edit-last-name"
                        value={editLastName}
                        onChange={(e) => setEditLastName(e.target.value)}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-phone">Phone</Label>
                      <Input
                        id="edit-phone"
                        value={editPhone}
                        onChange={(e) => setEditPhone(e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-country-code">Country *</Label>
                      <Select value={editCountryCode} onValueChange={setEditCountryCode} required>
                        <SelectTrigger id="edit-country-code">
                          <SelectValue placeholder="Select country" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="AF">Afghanistan</SelectItem>
                          <SelectItem value="LB">Lebanon</SelectItem>
                          <SelectItem value="EG">Egypt</SelectItem>
                          <SelectItem value="PS">Palestine</SelectItem>
                          <SelectItem value="SY">Syria</SelectItem>
                          <SelectItem value="TR">Turkey</SelectItem>
                          <SelectItem value="GB">United Kingdom</SelectItem>
                          <SelectItem value="JO">Jordan</SelectItem>
                          <SelectItem value="IQ">Iraq</SelectItem>
                          <SelectItem value="YE">Yemen</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2 col-span-2">
                      <Label htmlFor="edit-role">Role *</Label>
                      <Select value={editRoleId} onValueChange={setEditRoleId} required>
                        <SelectTrigger id="edit-role">
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                        <SelectContent>
                          {roles.map((role) => (
                            <SelectItem key={role.id} value={role.id}>
                              {role.display_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

            <DialogFooter>
              <Button type="submit" disabled={loading}>
                {loading ? 'Updating...' : 'Update User'}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setShowEditUser(false)
                  setEditingUser(null)
                  fetchUsers()
                }}
              >
                Cancel
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>

    {/* Password Reset Dialog */}
    <Dialog open={showPasswordReset} onOpenChange={(open) => {
      setShowPasswordReset(open)
      if (!open) {
        setResetPasswordUserId('')
        setResetPasswordUserName('')
        setNewPasswordReset('')
        setConfirmPasswordReset('')
        fetchUsers()
      }
    }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Reset Password: {resetPasswordUserName}</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleResetPassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password *</Label>
                    <Input
                      id="new-password"
                      type="password"
                      value={newPasswordReset}
                      onChange={(e) => setNewPasswordReset(e.target.value)}
                      placeholder="Min 8 characters, include uppercase, lowercase, and digit"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm Password *</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      value={confirmPasswordReset}
                      onChange={(e) => setConfirmPasswordReset(e.target.value)}
                      placeholder="Re-enter new password"
                      required
                    />
                  </div>

          <DialogFooter>
            <Button type="submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => {
                setShowPasswordReset(false)
                setResetPasswordUserId('')
                setResetPasswordUserName('')
                setNewPasswordReset('')
                setConfirmPasswordReset('')
                fetchUsers()
              }}
            >
              Cancel
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  </>
  )
}
