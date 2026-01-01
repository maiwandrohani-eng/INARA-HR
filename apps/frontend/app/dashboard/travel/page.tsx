'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Plane, Clock, CheckCircle, MapPin, Download, XCircle, Eye, Trash2 } from 'lucide-react'
import { TravelRequestForm } from '@/components/forms/TravelRequestForm'
import { travelService, type TravelRequest } from '@/services/travel.service'
import { useAuthStore } from '@/state/auth.store'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function TravelPage() {
  const [showTravelForm, setShowTravelForm] = useState(false)
  const [travelRequests, setTravelRequests] = useState<TravelRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRequest, setSelectedRequest] = useState<TravelRequest | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const { user } = useAuthStore()
  const isAdmin = user?.roles?.includes('admin') || user?.permissions?.includes('admin:all') || false

  useEffect(() => {
    loadTravelRequests()
  }, [])

  const loadTravelRequests = async () => {
    try {
      const requests = await travelService.getTravelRequests()
      setTravelRequests(requests || [])
    } catch (error) {
      console.error('Failed to load travel requests:', error)
      setTravelRequests([])
    } finally {
      setLoading(false)
    }
  }

  const handleNewRequest = () => {
    setShowTravelForm(true)
  }

  const handleExportPDF = async (requestId: string) => {
    try {
      const blob = await travelService.exportTravelRequestPDF(requestId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `travel_request_${requestId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to export PDF:', error)
      alert('Failed to export PDF. Please try again.')
    }
  }

  const handleApprove = async (requestId: string) => {
    if (!confirm('Approve this travel request?')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/travel/requests/${requestId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'approved' })
      })

      if (response.ok) {
        alert('Travel request approved successfully')
        loadTravelRequests()
      } else {
        alert('Failed to approve travel request')
      }
    } catch (error) {
      console.error('Failed to approve:', error)
      alert('Failed to approve travel request')
    }
  }

  const handleReject = async (requestId: string) => {
    if (!confirm('Reject this travel request?')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/travel/requests/${requestId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'rejected' })
      })

      if (response.ok) {
        alert('Travel request rejected')
        loadTravelRequests()
      } else {
        alert('Failed to reject travel request')
      }
    } catch (error) {
      console.error('Failed to reject:', error)
      alert('Failed to reject travel request')
    }
  }

  const handleViewDetails = (request: TravelRequest) => {
    setSelectedRequest(request)
    setShowDetailDialog(true)
  }

  const handleDelete = async (requestId: string) => {
    if (!confirm('Are you sure you want to delete this travel request? This action cannot be undone.')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/travel/requests/${requestId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok || response.status === 204) {
        alert('Travel request deleted successfully')
        loadTravelRequests()
      } else {
        const errorData = await response.json().catch(() => ({}))
        alert(errorData.detail || 'Failed to delete travel request')
      }
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Failed to delete travel request')
    }
  }

  const pendingRequests = (travelRequests || []).filter(r => r.status === 'pending')
  const approvedRequests = (travelRequests || []).filter(r => r.status === 'approved')

  const stats = [
    { label: 'Pending Requests', value: pendingRequests.length.toString(), icon: Clock, color: 'text-yellow-600' },
    { label: 'Approved Trips', value: approvedRequests.length.toString(), icon: CheckCircle, color: 'text-green-600' },
    { label: 'Total Requests', value: travelRequests.length.toString(), icon: MapPin, color: 'text-blue-600' },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Travel Management</h1>
          <p className="text-gray-500 mt-2">Manage travel requests and visa documentation</p>
        </div>
        <Button onClick={handleNewRequest}>
          <Plus className="w-4 h-4 mr-2" />
          New Travel Request
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
          <CardTitle>Travel Requests</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : travelRequests.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No travel requests found.</div>
          ) : (
            <div className="space-y-4">
              {travelRequests.map((request) => (
                <div key={request.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(request.status)}`}>
                          {request.status.toUpperCase()}
                        </span>
                        <span className="font-medium">{request.destination}</span>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        <p><strong>Purpose:</strong> {request.purpose}</p>
                        <p><strong>Duration:</strong> {request.start_date} to {request.end_date}</p>
                        {request.transport_mode && <p><strong>Transport:</strong> {request.transport_mode}</p>}
                        {request.estimated_cost && <p><strong>Estimated Cost:</strong> ${request.estimated_cost}</p>}
                      </div>
                    </div>
                    <div className="ml-4 flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewDetails(request)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View
                      </Button>
                      {request.status === 'pending' && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleApprove(request.id)}
                            className="bg-green-50 hover:bg-green-100 text-green-700 border-green-200"
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Approve
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleReject(request.id)}
                            className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </Button>
                        </>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExportPDF(request.id)}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export PDF
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(request.id)}
                          className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
              Travel Request Details
            </DialogTitle>
          </DialogHeader>
          {selectedRequest && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold text-gray-600">Status</label>
                  <div className="mt-1">
                    <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(selectedRequest.status)}`}>
                      {selectedRequest.status.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Employee</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.employee_name || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Destination</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.destination}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Purpose</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.purpose}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Start Date</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.start_date}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">End Date</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.end_date}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Duration</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.duration_days} days</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Transport Mode</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.transport_mode || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Estimated Cost</label>
                  <p className="mt-1 text-gray-900">${selectedRequest.estimated_cost || 0}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Accommodation Required</label>
                  <p className="mt-1 text-gray-900">{selectedRequest.accommodation_required ? 'Yes' : 'No'}</p>
                </div>
              </div>
              {selectedRequest.notes && (
                <div>
                  <label className="text-sm font-semibold text-gray-600">Notes</label>
                  <p className="mt-1 text-gray-900 bg-gray-50 p-3 rounded">{selectedRequest.notes}</p>
                </div>
              )}
              {selectedRequest.status === 'pending' && (
                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    onClick={() => {
                      handleApprove(selectedRequest.id)
                      setShowDetailDialog(false)
                    }}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve Request
                  </Button>
                  <Button
                    onClick={() => {
                      handleReject(selectedRequest.id)
                      setShowDetailDialog(false)
                    }}
                    variant="outline"
                    className="border-red-300 text-red-700 hover:bg-red-50"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject Request
                  </Button>
                  <Button
                    onClick={() => handleExportPDF(selectedRequest.id)}
                    variant="outline"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export PDF
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <TravelRequestForm 
        open={showTravelForm} 
        onOpenChange={setShowTravelForm}
        onSubmitSuccess={loadTravelRequests}
      />
    </div>
  )
}
