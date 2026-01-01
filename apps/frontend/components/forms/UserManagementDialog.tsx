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
import { Users, Shield, Trash2, Plus, Edit, Key, Download, RefreshCw, Eye, EyeOff } from 'lucide-react'

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

interface Employee {
  id: string
  employee_number: string
  full_name: string
  email: string
  department: string | null
  position: string | null
}

export function UserManagementDialog({ open, onOpenChange }: UserManagementDialogProps) {
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [showAddUser, setShowAddUser] = useState(false)
  const [roles, setRoles] = useState<any[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  
  // Add user form
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newFirstName, setNewFirstName] = useState('')
  const [newLastName, setNewLastName] = useState('')
  const [newPhone, setNewPhone] = useState('')
  const [newCountryCode, setNewCountryCode] = useState('')
  const [newRoleId, setNewRoleId] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [generatedPassword, setGeneratedPassword] = useState('')

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
      fetchEmployeesWithoutUsers()
    }
  }, [open])

  const fetchEmployeesWithoutUsers = async () => {
    try {
      const data = await api.get('/auth/employees/without-users')
      setEmployees(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching employees:', error)
      setEmployees([])
    }
  }

  const generatePassword = () => {
    // Generate a secure password (12 chars: uppercase, lowercase, digits, special)
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    let password = ''
    // Ensure at least one from each category
    password += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)]
    password += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)]
    password += '0123456789'[Math.floor(Math.random() * 10)]
    password += '!@#$%^&*'[Math.floor(Math.random() * 8)]
    // Fill the rest
    for (let i = password.length; i < 12; i++) {
      password += chars[Math.floor(Math.random() * chars.length)]
    }
    // Shuffle
    password = password.split('').sort(() => Math.random() - 0.5).join('')
    setNewPassword(password)
    setGeneratedPassword(password)
    return password
  }

  const handleEmployeeSelect = (employeeId: string) => {
    setSelectedEmployeeId(employeeId)
    const employee = employees.find(emp => emp.id === employeeId)
    if (employee) {
      setNewEmail(employee.email || '')
      const nameParts = employee.full_name.split(' ')
      setNewFirstName(nameParts[0] || '')
      setNewLastName(nameParts.slice(1).join(' ') || '')
      // Auto-generate password when employee is selected
      generatePassword()
    }
  }

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
      if (!newEmail || !newFirstName || !newLastName || !newCountryCode || !newRoleId) {
        alert('Please fill in all required fields')
        setLoading(false)
        return
      }

      // Auto-generate password if not provided
      if (!newPassword) {
        const generated = generatePassword()
        // Continue with generated password
      }

      const userData: any = {
        email: newEmail,
        first_name: newFirstName,
        last_name: newLastName,
        phone: newPhone || null,
        country_code: newCountryCode,
        role_ids: [newRoleId],
      }

      // Only include password if provided (otherwise backend will auto-generate)
      if (newPassword) {
        userData.password = newPassword
      }

      // Include employee_id if selected
      if (selectedEmployeeId) {
        userData.employee_id = selectedEmployeeId
      }

      const response = await api.post('/auth/register', userData)

      // Show generated password if available
      const password = response.generated_password || newPassword
      alert(`User created successfully!\n\nEmail: ${response.email}\nPassword: ${password}\n\nPlease save this password and share it with the user.`)
      setShowAddUser(false)
      resetAddForm()
      fetchUsers()
      fetchEmployeesWithoutUsers()
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
    setSelectedEmployeeId('')
    setNewEmail('')
    setNewFirstName('')
    setNewLastName('')
    setNewPhone('')
    setNewCountryCode('')
    setNewRoleId('')
    setNewPassword('')
    setGeneratedPassword('')
    setShowPassword(false)
  }

  const handleExportUsers = async () => {
    if (!confirm('This will reset all user passwords and generate new ones. The CSV file will contain the new passwords. Continue?')) {
      return
    }

    try {
      setLoading(true)
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const token = localStorage.getItem('access_token')
      
      const response = await fetch(`${API_URL}/auth/users/export`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to export users')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'users_credentials_export.csv'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      alert('Users exported successfully! All passwords have been reset and new passwords are in the CSV file.')
    } catch (error: any) {
      console.error('Error exporting users:', error)
      alert(`Failed to export users: ${error.message || 'Please try again'}`)
    } finally {
      setLoading(false)
    }
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
          {/* Action Buttons */}
          <div className="flex gap-3 justify-end">
            <Button 
              variant="outline"
              onClick={handleExportUsers}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Users with Credentials
            </Button>
            {!showAddUser && (
              <Button onClick={() => setShowAddUser(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add New User
              </Button>
            )}
          </div>

          {/* Add User Section */}
          {showAddUser ? (
            <form onSubmit={handleAddUser} className="border rounded-lg p-4 space-y-4">
              <h3 className="text-lg font-semibold">Add New User</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="employee">Select Employee (Optional)</Label>
                  <Select 
                    value={selectedEmployeeId || undefined} 
                    onValueChange={handleEmployeeSelect}
                  >
                    <SelectTrigger id="employee">
                      <SelectValue placeholder={employees.length === 0 ? "No employees available without user accounts" : "Select an employee to auto-fill details"} />
                    </SelectTrigger>
                    <SelectContent>
                      {employees.length === 0 ? (
                        <div className="px-2 py-1.5 text-sm text-gray-500">
                          No employees available without user accounts
                        </div>
                      ) : (
                        employees.map((emp) => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.full_name} ({emp.employee_number}) - {emp.email}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500">
                    Select an employee to auto-fill their details. Password will be auto-generated.
                  </p>
                </div>

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
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password">Password *</Label>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={generatePassword}
                      className="text-xs"
                    >
                      <RefreshCw className="w-3 h-3 mr-1" />
                      Generate Password
                    </Button>
                  </div>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Min 8 characters, include uppercase, lowercase, and digit"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  {generatedPassword && (
                    <p className="text-xs text-green-600">
                      ✓ Password auto-generated: {showPassword ? generatedPassword : '••••••••••••'}
                    </p>
                  )}
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
          ) : null}

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
