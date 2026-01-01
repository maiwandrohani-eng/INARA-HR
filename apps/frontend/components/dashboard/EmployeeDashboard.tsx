'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Calendar, 
  Clock, 
  FileText, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  XCircle,
  DollarSign,
  Plane,
  Shield,
  Award,
  BookOpen,
  Download
} from 'lucide-react'
import { useEffect, useState } from 'react'

interface LeaveRequest {
  id: string
  leave_type: string
  start_date: string
  end_date: string
  status: 'pending' | 'approved' | 'rejected'
  days: number
}

interface TravelRequest {
  id: string
  destination: string
  start_date: string
  end_date: string
  status: 'pending' | 'approved' | 'rejected'
}

interface Payslip {
  id: string
  payroll_id: string
  period: string
  amount: number
  currency: string
  status: string
}

interface EmployeeDashboardData {
  employee: {
    id: string
    name: string
    position: string
    department: string
    employee_number: string
  }
  leaveBalance: {
    annual: number
    sick: number
    total: number
  }
  recentLeaveRequests: LeaveRequest[]
  recentTravelRequests: TravelRequest[]
  recentPayslips: Payslip[]
  attendance: {
    present: number
    absent: number
    late: number
    total: number
  }
  grievances: {
    total: number
    resolved: number
    pending: number
  }
  performance: {
    lastReviewDate: string
    rating: string
    nextReviewDate: string
  }
  approvals?: {
    total_pending: number
    leave_pending: number
    travel_pending: number
    timesheet_pending: number
    performance_pending: number
  }
}

interface EmployeeDashboardProps {
  showSupervisorSection?: boolean
}

export function EmployeeDashboard({ showSupervisorSection = false }: EmployeeDashboardProps) {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<EmployeeDashboardData | null>(null)

  useEffect(() => {
    fetchEmployeeDashboardData()
  }, [])

  const fetchEmployeeDashboardData = async () => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${baseUrl}/dashboard/employee`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const dashboardData = await response.json()
        console.log('Dashboard data:', dashboardData)
        setData(dashboardData)
      } else {
        const errorData = await response.json()
        console.error('Dashboard API error:', errorData)
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPayslip = async (payrollId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${baseUrl}/payroll/${payrollId}/my-payslip`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `payslip_${Date.now()}.pdf`;
      
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download payslip:', error);
      alert('Failed to download payslip. Please try again.');
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge className="bg-green-500"><CheckCircle className="w-3 h-3 mr-1" />Approved</Badge>
      case 'rejected':
        return <Badge className="bg-red-500"><XCircle className="w-3 h-3 mr-1" />Rejected</Badge>
      case 'pending':
        return <Badge className="bg-yellow-500"><Clock className="w-3 h-3 mr-1" />Pending</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-pink-600 to-cyan-600 rounded-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">Welcome back, {data?.employee.name || 'Employee'}!</h1>
            <p className="mt-2 text-pink-100">
              {data?.employee.position} • {data?.employee.department}
            </p>
            <p className="text-sm text-pink-100">Employee ID: {data?.employee.employee_number}</p>
          </div>
          <Button 
            variant="secondary" 
            className="bg-white text-pink-600 hover:bg-pink-50 font-semibold"
            onClick={() => window.location.href = '/dashboard/my-personal-file'}
          >
            <FileText className="w-4 h-4 mr-2" />
            My Personnel File
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 border-pink-200 bg-gradient-to-br from-pink-50 to-cyan-50" onClick={() => window.location.href = '/dashboard/my-personal-file'}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-gray-700">My Personnel File</CardTitle>
            <FileText className="w-5 h-5 text-pink-600" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-gray-900">View Details</div>
            <p className="text-sm text-gray-600">Contracts, Documents & Records</p>
            <div className="mt-2 flex items-center text-xs text-pink-600 font-medium">
              Quick Access →
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Leave Balance</CardTitle>
            <Calendar className="w-5 h-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.leaveBalance.total || 0}</div>
            <p className="text-sm text-gray-500">
              Annual: {data?.leaveBalance.annual || 0} | Sick: {data?.leaveBalance.sick || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Attendance Rate</CardTitle>
            <Clock className="w-5 h-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {data?.attendance.total 
                ? Math.round((data.attendance.present / data.attendance.total) * 100)
                : 0}%
            </div>
            <p className="text-sm text-gray-500">
              {data?.attendance.present || 0} of {data?.attendance.total || 0} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Pending Requests</CardTitle>
            <AlertCircle className="w-5 h-5 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(data?.recentLeaveRequests.filter(r => r.status === 'pending').length || 0) +
               (data?.recentTravelRequests.filter(r => r.status === 'pending').length || 0)}
            </div>
            <p className="text-sm text-gray-500">Awaiting approval</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Performance</CardTitle>
            <Award className="w-5 h-5 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.performance.rating || 'N/A'}</div>
            <p className="text-sm text-gray-500">Last review rating</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leave Requests */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              My Leave Requests
            </CardTitle>
            <Button variant="outline" size="sm">View All</Button>
          </CardHeader>
          <CardContent>
            {data?.recentLeaveRequests.length ? (
              <div className="space-y-3">
                {data.recentLeaveRequests.slice(0, 5).map((leave) => (
                  <div key={leave.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{leave.leave_type}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(leave.start_date).toLocaleDateString()} - {new Date(leave.end_date).toLocaleDateString()}
                        <span className="ml-2">({leave.days} days)</span>
                      </p>
                    </div>
                    {getStatusBadge(leave.status)}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No leave requests</p>
            )}
          </CardContent>
        </Card>

        {/* Travel Requests */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Plane className="w-5 h-5" />
              My Travel Requests
            </CardTitle>
            <Button variant="outline" size="sm">View All</Button>
          </CardHeader>
          <CardContent>
            {data?.recentTravelRequests.length ? (
              <div className="space-y-3">
                {data.recentTravelRequests.slice(0, 5).map((travel) => (
                  <div key={travel.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{travel.destination}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(travel.start_date).toLocaleDateString()} - {new Date(travel.end_date).toLocaleDateString()}
                      </p>
                    </div>
                    {getStatusBadge(travel.status)}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No travel requests</p>
            )}
          </CardContent>
        </Card>

        {/* Recent Payslips */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Recent Payslips
            </CardTitle>
            <Button variant="outline" size="sm">View All</Button>
          </CardHeader>
          <CardContent>
            {data?.recentPayslips.length ? (
              <div className="space-y-3">
                {data.recentPayslips.slice(0, 5).map((payslip) => (
                  <div key={payslip.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex-1">
                      <p className="font-medium">{payslip.period}</p>
                      <p className="text-sm text-gray-500">
                        {payslip.currency} {payslip.amount.toLocaleString()}
                      </p>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleDownloadPayslip(payslip.payroll_id)}
                    >
                      <FileText className="w-4 h-4 mr-1" />
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No payslips available</p>
            )}
          </CardContent>
        </Card>

        {/* Grievances & Issues */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Grievances & Safeguarding
            </CardTitle>
            <Button variant="outline" size="sm">Submit New</Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium">Total Grievances</p>
                  <p className="text-2xl font-bold">{data?.grievances.total || 0}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-gray-400" />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 border rounded-lg">
                  <p className="text-sm text-gray-500">Resolved</p>
                  <p className="text-xl font-bold text-green-600">{data?.grievances.resolved || 0}</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <p className="text-sm text-gray-500">Pending</p>
                  <p className="text-xl font-bold text-yellow-600">{data?.grievances.pending || 0}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Manual Section */}
      <Card className="border-2 border-pink-200 bg-gradient-to-br from-pink-50 to-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-pink-600" />
            User Manual & Help
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => window.location.href = '/dashboard/user-manual'}
            variant="outline"
            className="w-full"
          >
            <BookOpen className="w-4 h-4 mr-2" />
            View User Manual
          </Button>
          <p className="text-sm text-gray-600 mt-4">
            Need help? Access the comprehensive user manual for step-by-step guides on using all system features.
          </p>
        </CardContent>
      </Card>

      {/* Performance Review Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Performance Review
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Last Review</p>
              <p className="text-lg font-semibold">
                {data?.performance.lastReviewDate 
                  ? new Date(data.performance.lastReviewDate).toLocaleDateString()
                  : 'Not yet reviewed'}
              </p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Current Rating</p>
              <p className="text-lg font-semibold">{data?.performance.rating || 'N/A'}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Next Review</p>
              <p className="text-lg font-semibold">
                {data?.performance.nextReviewDate 
                  ? new Date(data.performance.nextReviewDate).toLocaleDateString()
                  : 'Not scheduled'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Supervisor Approvals Section */}
      {showSupervisorSection && data?.approvals && (
        <>
          <div className="border-t-2 border-gray-200 my-8"></div>
          
          <div>
            <h2 className="text-2xl font-bold mb-4">Pending Approvals</h2>
            <p className="text-gray-500 mb-6">Review and approve requests from your team</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => window.location.href = '/dashboard/leave'}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Leave Requests</p>
                    <p className="text-3xl font-bold text-blue-600">{data.approvals.leave_pending}</p>
                  </div>
                  <Calendar className="w-12 h-12 text-blue-500" />
                </div>
                <Button variant="link" className="mt-2 px-0">View All →</Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => window.location.href = '/dashboard/travel'}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Travel Requests</p>
                    <p className="text-3xl font-bold text-purple-600">{data.approvals.travel_pending}</p>
                  </div>
                  <Plane className="w-12 h-12 text-purple-500" />
                </div>
                <Button variant="link" className="mt-2 px-0">View All →</Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => window.location.href = '/dashboard/timesheets'}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Timesheets</p>
                    <p className="text-3xl font-bold text-green-600">{data.approvals.timesheet_pending}</p>
                  </div>
                  <Clock className="w-12 h-12 text-green-500" />
                </div>
                <Button variant="link" className="mt-2 px-0">View All →</Button>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => window.location.href = '/dashboard/performance'}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Performance</p>
                    <p className="text-3xl font-bold text-orange-600">{data.approvals.performance_pending}</p>
                  </div>
                  <Award className="w-12 h-12 text-orange-500" />
                </div>
                <Button variant="link" className="mt-2 px-0">View All →</Button>
              </CardContent>
            </Card>
          </div>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Recent Approval Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No pending approval requests at the moment</p>
                <p className="text-sm mt-2">New requests from your team will appear here</p>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
