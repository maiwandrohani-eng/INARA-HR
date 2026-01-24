'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Calendar, 
  Clock, 
  CheckCircle,
  XCircle,
  AlertTriangle,
  Plane,
  FileText,
  UserCheck,
  TrendingUp
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { PendingApprovalsWidget } from './PendingApprovalsWidget'

interface PendingLeaveRequest {
  id: string
  employee_name: string
  employee_id: string
  leave_type: string
  start_date: string
  end_date: string
  days: number
  reason: string
  submitted_date: string
}

interface PendingTravelRequest {
  id: string
  employee_name: string
  employee_id: string
  destination: string
  purpose: string
  start_date: string
  end_date: string
  submitted_date: string
}

interface TeamMember {
  id: string
  name: string
  position: string
  attendance_rate: number
  leave_balance: number
  status: string
}

interface SupervisorDashboardData {
  supervisor: {
    id: string
    name: string
    position: string
    team_size: number
  }
  pendingLeaveRequests: PendingLeaveRequest[]
  pendingTravelRequests: PendingTravelRequest[]
  teamMembers: TeamMember[]
  teamStats: {
    totalMembers: number
    activeMembers: number
    onLeave: number
    avgAttendance: number
  }
  complianceItems: {
    pending: number
    overdue: number
  }
}

export function SupervisorDashboard() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<SupervisorDashboardData | null>(null)

  useEffect(() => {
    fetchSupervisorDashboardData()
  }, [])

  const fetchSupervisorDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/supervisor`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const dashboardData = await response.json()
        setData(dashboardData)
      }
    } catch (error) {
      console.error('Error fetching supervisor dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApproveLeave = async (requestId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leave/requests/${requestId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        alert('Leave request approved successfully')
        fetchSupervisorDashboardData()
      }
    } catch (error) {
      console.error('Error approving leave:', error)
      alert('Failed to approve leave request')
    }
  }

  const handleRejectLeave = async (requestId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leave/requests/${requestId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        alert('Leave request rejected')
        fetchSupervisorDashboardData()
      }
    } catch (error) {
      console.error('Error rejecting leave:', error)
      alert('Failed to reject leave request')
    }
  }

  const handleApproveTravel = async (requestId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/travel/requests/${requestId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        alert('Travel request approved successfully')
        fetchSupervisorDashboardData()
      }
    } catch (error) {
      console.error('Error approving travel:', error)
      alert('Failed to approve travel request')
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      {/* Supervisor Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold">Supervisor Dashboard</h1>
        <p className="mt-2 text-purple-100">
          {data?.supervisor.position} • Managing {data?.supervisor.team_size || 0} team members
        </p>
      </div>

      {/* Team Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Team Members</CardTitle>
            <Users className="w-5 h-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.teamStats.totalMembers || 0}</div>
            <p className="text-sm text-gray-500">
              {data?.teamStats.activeMembers || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Pending Approvals</CardTitle>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(data?.pendingLeaveRequests.length || 0) + (data?.pendingTravelRequests.length || 0)}
            </div>
            <p className="text-sm text-gray-500">Requires your action</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Team Attendance</CardTitle>
            <UserCheck className="w-5 h-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.teamStats.avgAttendance || 0}%</div>
            <p className="text-sm text-gray-500">Average rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">On Leave</CardTitle>
            <Calendar className="w-5 h-5 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.teamStats.onLeave || 0}</div>
            <p className="text-sm text-gray-500">Members currently away</p>
          </CardContent>
        </Card>
      </div>

      {/* Unified Pending Approvals Widget */}
      <PendingApprovalsWidget />

      {/* Pending Approvals Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Leave Requests */}
        <Card className="border-yellow-200 border-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-700">
              <Calendar className="w-5 h-5" />
              Pending Leave Requests
              {data?.pendingLeaveRequests.length ? (
                <Badge className="bg-yellow-500">{data.pendingLeaveRequests.length}</Badge>
              ) : null}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.pendingLeaveRequests.length ? (
              <div className="space-y-4">
                {data.pendingLeaveRequests.map((request) => (
                  <div key={request.id} className="p-4 border rounded-lg bg-yellow-50">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-semibold text-lg">{request.employee_name}</p>
                        <p className="text-sm text-gray-600">{request.leave_type}</p>
                      </div>
                      <Badge variant="outline" className="bg-white">
                        {request.days} days
                      </Badge>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <p className="text-sm">
                        <span className="font-medium">Period:</span>{' '}
                        {new Date(request.start_date).toLocaleDateString()} -{' '}
                        {new Date(request.end_date).toLocaleDateString()}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Reason:</span> {request.reason}
                      </p>
                      <p className="text-xs text-gray-500">
                        Submitted: {new Date(request.submitted_date).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        className="flex-1 bg-green-600 hover:bg-green-700"
                        onClick={() => handleApproveLeave(request.id)}
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive" 
                        className="flex-1"
                        onClick={() => handleRejectLeave(request.id)}
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No pending leave requests</p>
            )}
          </CardContent>
        </Card>

        {/* Pending Travel Requests */}
        <Card className="border-blue-200 border-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700">
              <Plane className="w-5 h-5" />
              Pending Travel Requests
              {data?.pendingTravelRequests.length ? (
                <Badge className="bg-blue-500">{data.pendingTravelRequests.length}</Badge>
              ) : null}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data?.pendingTravelRequests.length ? (
              <div className="space-y-4">
                {data.pendingTravelRequests.map((request) => (
                  <div key={request.id} className="p-4 border rounded-lg bg-blue-50">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-semibold text-lg">{request.employee_name}</p>
                        <p className="text-sm text-gray-600">{request.destination}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <p className="text-sm">
                        <span className="font-medium">Travel Dates:</span>{' '}
                        {new Date(request.start_date).toLocaleDateString()} -{' '}
                        {new Date(request.end_date).toLocaleDateString()}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Purpose:</span> {request.purpose}
                      </p>
                      <p className="text-xs text-gray-500">
                        Submitted: {new Date(request.submitted_date).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        className="flex-1 bg-green-600 hover:bg-green-700"
                        onClick={() => handleApproveTravel(request.id)}
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Approve
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive" 
                        className="flex-1"
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Reject
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                      >
                        <FileText className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No pending travel requests</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Team Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Team Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data?.teamMembers.length ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Employee</th>
                    <th className="text-left py-3 px-4">Position</th>
                    <th className="text-center py-3 px-4">Attendance</th>
                    <th className="text-center py-3 px-4">Leave Balance</th>
                    <th className="text-center py-3 px-4">Status</th>
                    <th className="text-center py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.teamMembers.map((member) => (
                    <tr key={member.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{member.name}</td>
                      <td className="py-3 px-4 text-gray-600">{member.position}</td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant="outline" className={
                          member.attendance_rate >= 95 ? 'bg-green-50 text-green-700' :
                          member.attendance_rate >= 85 ? 'bg-yellow-50 text-yellow-700' :
                          'bg-red-50 text-red-700'
                        }>
                          {member.attendance_rate}%
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">{member.leave_balance} days</td>
                      <td className="py-3 px-4 text-center">
                        <Badge className={
                          member.status === 'active' ? 'bg-green-500' :
                          member.status === 'on_leave' ? 'bg-yellow-500' :
                          'bg-gray-500'
                        }>
                          {member.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Button variant="ghost" size="sm">
                          <TrendingUp className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No team members</p>
          )}
        </CardContent>
      </Card>

      {/* Compliance Items */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Compliance & Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg bg-yellow-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending Reviews</p>
                  <p className="text-3xl font-bold text-yellow-700">{data?.complianceItems.pending || 0}</p>
                </div>
                <Clock className="w-10 h-10 text-yellow-500" />
              </div>
            </div>
            
            <div className="p-4 border rounded-lg bg-red-50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overdue Items</p>
                  <p className="text-3xl font-bold text-red-700">{data?.complianceItems.overdue || 0}</p>
                </div>
                <AlertTriangle className="w-10 h-10 text-red-500" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
