'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Calendar, Clock, CheckCircle, XCircle, Upload, Download } from 'lucide-react'
import { LeaveRequestForm } from '@/components/forms/LeaveRequestForm'
import { exportLeaveTemplate } from '@/utils/excelExport'
import { leaveService, type LeaveRequest } from '@/services/leave.service'

export default function LeavePage() {
  const [showLeaveForm, setShowLeaveForm] = useState(false)
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadLeaveRequests()
  }, [])

  const loadLeaveRequests = async () => {
    try {
      const requests = await leaveService.getLeaveRequests()
      setLeaveRequests(requests)
    } catch (error) {
      console.error('Failed to load leave requests:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRequestLeave = () => {
    setShowLeaveForm(true)
  }

  const handleExportTemplate = () => {
    exportLeaveTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to submit multiple leave requests.')
  }

  const handleExportPDF = async (requestId: string) => {
    try {
      const blob = await leaveService.exportLeaveRequestPDF(requestId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `leave_request_${requestId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to export PDF:', error)
      alert('Failed to export PDF. Please try again.')
    }
  }

  const pendingRequests = leaveRequests.filter(r => r.status === 'pending')
  const approvedThisMonth = leaveRequests.filter(r => r.status === 'approved')
  const rejectedRequests = leaveRequests.filter(r => r.status === 'rejected')

  const stats = [
    { label: 'Pending Requests', value: pendingRequests.length.toString(), icon: Clock, color: 'text-yellow-600' },
    { label: 'Approved This Month', value: approvedThisMonth.length.toString(), icon: CheckCircle, color: 'text-green-600' },
    { label: 'Rejected', value: rejectedRequests.length.toString(), icon: XCircle, color: 'text-red-600' },
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
          <h1 className="text-3xl font-bold">Leave & Attendance</h1>
          <p className="text-gray-500 mt-2">Manage leave requests and attendance records</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportTemplate}>
            <Upload className="w-4 h-4 mr-2" />
            Export Template
          </Button>
          <Button onClick={handleRequestLeave}>
            <Plus className="w-4 h-4 mr-2" />
            Request Leave
          </Button>
        </div>
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

      <div className="grid grid-cols-1 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Leave Requests</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-gray-500">
                Loading...
              </div>
            ) : leaveRequests.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No leave requests found.
              </div>
            ) : (
              <div className="space-y-4">
                {leaveRequests.map((request) => (
                  <div key={request.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(request.status)}`}>
                            {request.status.toUpperCase()}
                          </span>
                          <span className="font-medium">{request.leave_type}</span>
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          <p><strong>Duration:</strong> {request.start_date} to {request.end_date} ({request.total_days} days)</p>
                          {request.reason && <p><strong>Reason:</strong> {request.reason}</p>}
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
      </div>

      <LeaveRequestForm open={showLeaveForm} onOpenChange={setShowLeaveForm} />
    </div>
  )
}
