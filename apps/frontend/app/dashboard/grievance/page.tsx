export const dynamic = "force-dynamic";

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, FileText, Clock, CheckCircle, Eye } from 'lucide-react'
import { GrievanceForm } from '@/components/forms/GrievanceForm'

interface Grievance {
  id: string
  case_number: string
  employee_id: string
  grievance_type: string
  description: string
  filed_date: string
  status: string
  resolution?: string
  resolution_date?: string
}

export default function GrievancePage() {
  const [showGrievanceForm, setShowGrievanceForm] = useState(false)
  const [grievances, setGrievances] = useState<Grievance[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedGrievance, setSelectedGrievance] = useState<Grievance | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [editFormData, setEditFormData] = useState({
    status: '',
    resolution: '',
    resolution_date: ''
  })

  useEffect(() => {
    fetchGrievances()
  }, [])

  const fetchGrievances = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        console.error('No access token found')
        setLoading(false)
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/grievances/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setGrievances(data)
      } else {
        console.error('Failed to fetch grievances:', response.status)
      }
    } catch (error) {
      console.error('Failed to fetch grievances:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileGrievance = () => {
    setShowGrievanceForm(true)
  }

  const handleGrievanceSubmitted = () => {
    setShowGrievanceForm(false)
    fetchGrievances()
  }

  const handleEditGrievance = () => {
    if (selectedGrievance) {
      setEditFormData({
        status: selectedGrievance.status,
        resolution: selectedGrievance.resolution || '',
        resolution_date: selectedGrievance.resolution_date || ''
      })
      setIsEditMode(true)
    }
  }

  const handleUpdateGrievance = async () => {
    if (!selectedGrievance) return

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Please log in again')
        return
      }

      const response = await fetch(`http://localhost:8000/api/v1/grievances/${selectedGrievance.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editFormData)
      })

      if (response.ok) {
        alert('Grievance updated successfully')
        setIsEditMode(false)
        setSelectedGrievance(null)
        fetchGrievances()
      } else {
        const error = await response.text()
        alert(`Failed to update grievance: ${error}`)
      }
    } catch (error) {
      console.error('Failed to update grievance:', error)
      alert('Failed to update grievance')
    }
  }

  const openGrievances = grievances.filter(g => g.status === 'open' || g.status === 'pending').length
  const underReview = grievances.filter(g => g.status === 'investigating' || g.status === 'under_review').length
  const resolved = grievances.filter(g => g.status === 'resolved' || g.status === 'closed').length

  const stats = [
    { label: 'Open Grievances', value: String(openGrievances), icon: FileText, color: 'text-orange-600' },
    { label: 'Under Review', value: String(underReview), icon: Clock, color: 'text-yellow-600' },
    { label: 'Resolved', value: String(resolved), icon: CheckCircle, color: 'text-green-600' },
  ]

  const getStatusBadge = (status: string) => {
    const colors = {
      open: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      investigating: 'bg-blue-100 text-blue-800',
      under_review: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Grievance Management</h1>
          <p className="text-gray-500 mt-2">Handle employee grievances and disciplinary actions</p>
        </div>
        <Button onClick={handleFileGrievance}>
          <Plus className="w-4 h-4 mr-2" />
          File Grievance
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-3xl font-bold mt-2">{stat.value}</p>
                </div>
                <stat.icon className={`w-12 h-12 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Grievances</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : grievances.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No grievances filed recently.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Case Number</th>
                    <th className="text-left py-3 px-4">Type</th>
                    <th className="text-left py-3 px-4">Filed Date</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {grievances.map((grievance) => (
                    <tr key={grievance.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{grievance.case_number}</td>
                      <td className="py-3 px-4 capitalize">{grievance.grievance_type.replace(/_/g, ' ')}</td>
                      <td className="py-3 px-4">{new Date(grievance.filed_date).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(grievance.status)}`}>
                          {grievance.status.charAt(0).toUpperCase() + grievance.status.slice(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedGrievance(grievance)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <GrievanceForm 
        open={showGrievanceForm} 
        onOpenChange={setShowGrievanceForm}
        onSubmitSuccess={handleGrievanceSubmitted}
      />

      {/* Grievance Detail Modal */}
      {selectedGrievance && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">Case {selectedGrievance.case_number}</h2>
                <p className="text-sm text-gray-500">Filed on {new Date(selectedGrievance.filed_date).toLocaleDateString()}</p>
              </div>
              <Button variant="ghost" onClick={() => setSelectedGrievance(null)}>✕</Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Case Information */}
              <div className="border rounded-lg p-4 space-y-3">
                <h3 className="font-semibold text-lg">Grievance Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Type</label>
                    <p className="capitalize">{selectedGrievance.grievance_type.replace(/_/g, ' ')}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <p>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(selectedGrievance.status)}`}>
                        {selectedGrievance.status.charAt(0).toUpperCase() + selectedGrievance.status.slice(1)}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Filed Date</label>
                    <p>{new Date(selectedGrievance.filed_date).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Case Number</label>
                    <p className="font-mono">{selectedGrievance.case_number}</p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Description</label>
                  <p className="mt-1 whitespace-pre-wrap">{selectedGrievance.description}</p>
                </div>
              </div>

              {/* Resolution */}
              {selectedGrievance.resolution && (
                <div className="border rounded-lg p-4 space-y-3">
                  <h3 className="font-semibold text-lg">Resolution</h3>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Resolution Details</label>
                    <p className="mt-1 whitespace-pre-wrap">{selectedGrievance.resolution}</p>
                  </div>
                  {selectedGrievance.resolution_date && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Resolution Date</label>
                      <p>{new Date(selectedGrievance.resolution_date).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Edit Form or Actions */}
              {isEditMode ? (
                <div className="border rounded-lg p-4 space-y-4 bg-gray-50">
                  <h3 className="font-semibold text-lg">Update Grievance</h3>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <select 
                      className="w-full border rounded px-3 py-2"
                      value={editFormData.status}
                      onChange={(e) => setEditFormData({...editFormData, status: e.target.value})}
                    >
                      <option value="pending">Pending</option>
                      <option value="open">Open</option>
                      <option value="investigating">Investigating</option>
                      <option value="under_review">Under Review</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Resolution</label>
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      rows={4}
                      value={editFormData.resolution}
                      onChange={(e) => setEditFormData({...editFormData, resolution: e.target.value})}
                      placeholder="Enter resolution details..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Resolution Date</label>
                    <input 
                      type="date"
                      className="w-full border rounded px-3 py-2"
                      value={editFormData.resolution_date}
                      onChange={(e) => setEditFormData({...editFormData, resolution_date: e.target.value})}
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setIsEditMode(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleUpdateGrievance}>
                      Save Changes
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setSelectedGrievance(null)}>
                    Close
                  </Button>
                  <Button onClick={handleEditGrievance}>
                    Update Grievance
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
