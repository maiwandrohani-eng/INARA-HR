export const dynamic = "force-dynamic";

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Shield, AlertTriangle, Clock, CheckCircle, Eye, Trash2 } from 'lucide-react'
import { SafeguardingReportForm } from '@/components/forms/SafeguardingReportForm'
import { useAuthStore } from '@/state/auth.store'

interface SafeguardingCase {
  id: string
  case_number: string
  case_type: string
  severity: string
  status: string
  investigation_status: string
  reported_date: string
  description: string
  location?: string
  incident_date?: string
  investigation_findings?: string
  actions_taken?: string
  outcome?: string
}

export default function SafeguardingPage() {
  const [showReportForm, setShowReportForm] = useState(false)
  const [cases, setCases] = useState<SafeguardingCase[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCase, setSelectedCase] = useState<SafeguardingCase | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const { user } = useAuthStore()
  const isAdmin = user?.roles?.includes('admin') || user?.permissions?.includes('admin:all') || false
  const [editFormData, setEditFormData] = useState({
    status: '',
    investigation_status: '',
    investigation_findings: '',
    actions_taken: '',
    outcome: ''
  })

  useEffect(() => {
    fetchCases()
  }, [])

  const fetchCases = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        console.error('No access token found - user not logged in')
        setLoading(false)
        return
      }
      
      const response = await fetch('http://localhost:8000/api/v1/safeguarding/cases', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.status === 401) {
        console.error('Token expired - please log in again')
        alert('Your session has expired. Please log out and log back in.')
        setLoading(false)
        return
      }
      
      if (response.ok) {
        const data = await response.json()
        setCases(data)
      } else {
        console.error('Failed to fetch cases:', response.status)
      }
    } catch (error) {
      console.error('Failed to fetch cases:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReportCase = () => {
    setShowReportForm(true)
  }

  const handleReportSubmitted = () => {
    setShowReportForm(false)
    fetchCases() // Refresh the list
  }

  const handleEditCase = () => {
    if (selectedCase) {
      setEditFormData({
        status: selectedCase.status,
        investigation_status: selectedCase.investigation_status,
        investigation_findings: selectedCase.investigation_findings || '',
        actions_taken: selectedCase.actions_taken || '',
        outcome: selectedCase.outcome || ''
      })
      setIsEditMode(true)
    }
  }

  const handleUpdateCase = async () => {
    if (!selectedCase) return

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Please log in again')
        return
      }

      const response = await fetch(`http://localhost:8000/api/v1/safeguarding/cases/${selectedCase.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editFormData)
      })

      if (response.ok) {
        alert('Case updated successfully')
        setIsEditMode(false)
        setSelectedCase(null)
        fetchCases()
      } else {
        const error = await response.text()
        alert(`Failed to update case: ${error}`)
      }
    } catch (error) {
      console.error('Failed to update case:', error)
      alert('Failed to update case')
    }
  }

  const handleDelete = async (caseId: string) => {
    if (!confirm('Are you sure you want to delete this safeguarding case? This action cannot be undone.')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/safeguarding/cases/${caseId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok || response.status === 204) {
        alert('Safeguarding case deleted successfully')
        fetchCases()
      } else {
        const errorData = await response.json().catch(() => ({}))
        alert(errorData.detail || 'Failed to delete safeguarding case')
      }
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Failed to delete safeguarding case')
    }
  }

  // Calculate stats from actual data
  const openCases = cases.filter(c => c.status === 'open').length
  const investigatingCases = cases.filter(c => c.status === 'investigating').length
  const resolvedCases = cases.filter(c => c.status === 'resolved' || c.status === 'closed').length

  const stats = [
    { label: 'Open Cases', value: String(openCases), icon: AlertTriangle, color: 'text-red-600' },
    { label: 'Under Investigation', value: String(investigatingCases), icon: Shield, color: 'text-yellow-600' },
    { label: 'Resolved Cases', value: String(resolvedCases), icon: CheckCircle, color: 'text-green-600' },
  ]

  const activeCases = cases.filter(c => c.status === 'open' || c.status === 'investigating')

  const getSeverityBadge = (severity: string) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      open: 'bg-red-100 text-red-800',
      investigating: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Safeguarding</h1>
          <p className="text-gray-500 mt-2">Manage safeguarding cases and investigations</p>
        </div>
        <Button onClick={handleReportCase}>
          <Plus className="w-4 h-4 mr-2" />
          Report Case
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
          <CardTitle>Active Safeguarding Cases</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading cases...</div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Case Number</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reported</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {activeCases.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                        No active safeguarding cases.
                      </td>
                    </tr>
                  ) : (
                    activeCases.map((caseItem) => (
                      <tr key={caseItem.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {caseItem.case_number}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 capitalize">
                          {caseItem.case_type}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityBadge(caseItem.severity)}`}>
                            {caseItem.severity.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(caseItem.status)}`}>
                            {caseItem.status.charAt(0).toUpperCase() + caseItem.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {new Date(caseItem.reported_date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="flex gap-2">
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => setSelectedCase(caseItem)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            {isAdmin && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(caseItem.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <SafeguardingReportForm 
        open={showReportForm} 
        onOpenChange={setShowReportForm}
        onSubmitSuccess={handleReportSubmitted}
      />

      {/* Case Detail Modal */}
      {selectedCase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">Case {selectedCase.case_number}</h2>
                <p className="text-sm text-gray-500">Reported on {new Date(selectedCase.reported_date).toLocaleDateString()}</p>
              </div>
              <Button variant="ghost" onClick={() => setSelectedCase(null)}>✕</Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Case Information */}
              <div className="border rounded-lg p-4 space-y-3">
                <h3 className="font-semibold text-lg">Case Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Type</label>
                    <p className="capitalize">{selectedCase.case_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Severity</label>
                    <p>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityBadge(selectedCase.severity)}`}>
                        {selectedCase.severity.toUpperCase()}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <p>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(selectedCase.status)}`}>
                        {selectedCase.status.charAt(0).toUpperCase() + selectedCase.status.slice(1)}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Investigation Status</label>
                    <p className="capitalize">{selectedCase.investigation_status}</p>
                  </div>
                  {selectedCase.incident_date && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Incident Date</label>
                      <p>{new Date(selectedCase.incident_date).toLocaleDateString()}</p>
                    </div>
                  )}
                  {selectedCase.location && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Location</label>
                      <p>{selectedCase.location}</p>
                    </div>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Description</label>
                  <p className="mt-1 whitespace-pre-wrap">{selectedCase.description}</p>
                </div>
              </div>

              {/* Investigation */}
              <div className="border rounded-lg p-4 space-y-3">
                <h3 className="font-semibold text-lg">Investigation</h3>
                {selectedCase.investigation_findings ? (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Findings</label>
                    <p className="mt-1 whitespace-pre-wrap">{selectedCase.investigation_findings}</p>
                  </div>
                ) : (
                  <p className="text-gray-500 italic">No investigation findings recorded yet</p>
                )}
              </div>

              {/* Actions & Outcome */}
              <div className="border rounded-lg p-4 space-y-3">
                <h3 className="font-semibold text-lg">Actions & Outcome</h3>
                {selectedCase.actions_taken && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Actions Taken</label>
                    <p className="mt-1 whitespace-pre-wrap">{selectedCase.actions_taken}</p>
                  </div>
                )}
                {selectedCase.outcome && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Outcome</label>
                    <p className="mt-1 whitespace-pre-wrap">{selectedCase.outcome}</p>
                  </div>
                )}
                {!selectedCase.actions_taken && !selectedCase.outcome && (
                  <p className="text-gray-500 italic">No actions or outcomes recorded yet</p>
                )}
              </div>

              {/* Edit Form or Update Button */}
              {isEditMode ? (
                <div className="border rounded-lg p-4 space-y-4 bg-gray-50">
                  <h3 className="font-semibold text-lg">Update Case</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Status</label>
                      <select 
                        className="w-full border rounded px-3 py-2"
                        value={editFormData.status}
                        onChange={(e) => setEditFormData({...editFormData, status: e.target.value})}
                      >
                        <option value="open">Open</option>
                        <option value="investigating">Investigating</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-1">Investigation Status</label>
                      <select 
                        className="w-full border rounded px-3 py-2"
                        value={editFormData.investigation_status}
                        onChange={(e) => setEditFormData({...editFormData, investigation_status: e.target.value})}
                      >
                        <option value="not_started">Not Started</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Investigation Findings</label>
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      rows={4}
                      value={editFormData.investigation_findings}
                      onChange={(e) => setEditFormData({...editFormData, investigation_findings: e.target.value})}
                      placeholder="Enter investigation findings..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Actions Taken</label>
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      rows={3}
                      value={editFormData.actions_taken}
                      onChange={(e) => setEditFormData({...editFormData, actions_taken: e.target.value})}
                      placeholder="Enter actions taken..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Outcome</label>
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      rows={3}
                      value={editFormData.outcome}
                      onChange={(e) => setEditFormData({...editFormData, outcome: e.target.value})}
                      placeholder="Enter outcome..."
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setIsEditMode(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleUpdateCase}>
                      Save Changes
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setSelectedCase(null)}>
                    Close
                  </Button>
                  <Button onClick={handleEditCase}>
                    Update Case
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      />
    </div>
  )
}
