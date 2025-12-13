'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Plane, Clock, CheckCircle, MapPin, Download } from 'lucide-react'
import { TravelRequestForm } from '@/components/forms/TravelRequestForm'
import { travelService, type TravelRequest } from '@/services/travel.service'

export default function TravelPage() {
  const [showTravelForm, setShowTravelForm] = useState(false)
  const [travelRequests, setTravelRequests] = useState<TravelRequest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTravelRequests()
  }, [])

  const loadTravelRequests = async () => {
    try {
      const requests = await travelService.getTravelRequests()
      setTravelRequests(requests)
    } catch (error) {
      console.error('Failed to load travel requests:', error)
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

  const pendingRequests = travelRequests.filter(r => r.status === 'pending')
  const approvedRequests = travelRequests.filter(r => r.status === 'approved')

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
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExportPDF(request.id)}
                      className="ml-4"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export PDF
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <TravelRequestForm open={showTravelForm} onOpenChange={setShowTravelForm} />
    </div>
  )
}
