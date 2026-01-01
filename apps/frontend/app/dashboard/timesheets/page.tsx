export const dynamic = "force-dynamic";

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Clock, CheckCircle, AlertCircle, Download, Eye, XCircle, Trash2 } from 'lucide-react'
import { TimesheetForm } from '@/components/forms/TimesheetForm'
import { timesheetService, type Timesheet } from '@/services/timesheet.service'
import { useAuthStore } from '@/state/auth.store'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function TimesheetsPage() {
  const [showTimesheetForm, setShowTimesheetForm] = useState(false)
  const [timesheets, setTimesheets] = useState<Timesheet[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTimesheet, setSelectedTimesheet] = useState<Timesheet | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const { user } = useAuthStore()
  const isAdmin = user?.roles?.includes('admin') || user?.permissions?.includes('admin:all') || false

  useEffect(() => {
    loadTimesheets()
  }, [])

  const loadTimesheets = async () => {
    try {
      const data = await timesheetService.getTimesheets()
      setTimesheets(data)
    } catch (error) {
      console.error('Failed to load timesheets:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTimesheet = () => {
    setShowTimesheetForm(true)
  }

  const handleExportPDF = async (timesheetId: string) => {
    try {
      const blob = await timesheetService.exportTimesheetPDF(timesheetId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `timesheet_${timesheetId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to export PDF:', error)
      alert('Failed to export PDF. Please try again.')
    }
  }

  const handleApprove = async (timesheetId: string) => {
    if (!confirm('Approve this timesheet?')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/timesheets/${timesheetId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'approved' })
      })

      if (response.ok) {
        alert('Timesheet approved successfully')
        loadTimesheets()
      } else {
        alert('Failed to approve timesheet')
      }
    } catch (error) {
      console.error('Failed to approve:', error)
      alert('Failed to approve timesheet')
    }
  }

  const handleReject = async (timesheetId: string) => {
    if (!confirm('Reject this timesheet?')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/timesheets/${timesheetId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'rejected' })
      })

      if (response.ok) {
        alert('Timesheet rejected')
        loadTimesheets()
      } else {
        alert('Failed to reject timesheet')
      }
    } catch (error) {
      console.error('Failed to reject:', error)
      alert('Failed to reject timesheet')
    }
  }

  const handleViewDetails = (timesheet: Timesheet) => {
    setSelectedTimesheet(timesheet)
    setShowDetailDialog(true)
  }

  const handleDelete = async (timesheetId: string) => {
    if (!confirm('Are you sure you want to delete this timesheet? This action cannot be undone.')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/timesheets/${timesheetId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok || response.status === 204) {
        alert('Timesheet deleted successfully')
        loadTimesheets()
      } else {
        const errorData = await response.json().catch(() => ({}))
        alert(errorData.detail || 'Failed to delete timesheet')
      }
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Failed to delete timesheet')
    }
  }

  const pendingTimesheets = timesheets.filter(t => t.status === 'pending')
  const approvedTimesheets = timesheets.filter(t => t.status === 'approved')
  const totalHours = timesheets.reduce((sum, t) => sum + t.total_hours, 0)

  const stats = [
    { label: 'Pending Approval', value: pendingTimesheets.length.toString(), icon: AlertCircle, color: 'text-orange-600' },
    { label: 'Approved This Week', value: approvedTimesheets.length.toString(), icon: CheckCircle, color: 'text-green-600' },
    { label: 'Total Hours Logged', value: totalHours.toString(), icon: Clock, color: 'text-blue-600' },
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
          <h1 className="text-3xl font-bold">Timesheets</h1>
          <p className="text-gray-500 mt-2">Track and manage project time entries</p>
        </div>
        <Button onClick={handleAddTimesheet}>
          <Plus className="w-4 h-4 mr-2" />
          New Timesheet
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
          <CardTitle>Recent Timesheets</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : timesheets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No timesheets submitted yet.</div>
          ) : (
            <div className="border rounded-lg">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hours</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entries</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {timesheets.map((timesheet) => (
                    <tr key={timesheet.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3">{timesheet.start_date} - {timesheet.end_date}</td>
                      <td className="px-4 py-3">{timesheet.total_hours}</td>
                      <td className="px-4 py-3">{timesheet.entries?.length || 0} entries</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(timesheet.status)}`}>
                          {timesheet.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewDetails(timesheet)}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                          {(timesheet.status === 'submitted' || timesheet.status === 'pending') && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleApprove(timesheet.id)}
                                className="bg-green-50 hover:bg-green-100 text-green-700 border-green-200"
                              >
                                <CheckCircle className="w-4 h-4 mr-1" />
                                Approve
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleReject(timesheet.id)}
                                className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                              >
                                <AlertCircle className="w-4 h-4 mr-1" />
                                Reject
                              </Button>
                            </>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleExportPDF(timesheet.id)}
                          >
                            <Download className="w-4 h-4 mr-1" />
                            Export
                          </Button>
                          {isAdmin && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(timesheet.id)}
                              className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Delete
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-[95vw] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
              Monthly Timesheet - Review
            </DialogTitle>
          </DialogHeader>
          {selectedTimesheet && (
            <div className="space-y-4">
              {/* Status Badge */}
              <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                <div>
                  <span className="text-sm text-gray-600">Status: </span>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(selectedTimesheet.status)}`}>
                    {selectedTimesheet.status.toUpperCase()}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  Submitted: {selectedTimesheet.submitted_date || 'N/A'}
                </div>
              </div>

              {/* Employee Information */}
              <div className="grid grid-cols-4 gap-3 bg-gray-50 p-4 rounded-lg text-sm">
                <div>
                  <label className="font-semibold text-gray-600">Employee</label>
                  <p className="mt-1 text-gray-900">{selectedTimesheet.employee || 'N/A'}</p>
                </div>
                <div>
                  <label className="font-semibold text-gray-600">Period</label>
                  <p className="mt-1 text-gray-900">
                    {selectedTimesheet.period_start || selectedTimesheet.start_date} to {selectedTimesheet.period_end || selectedTimesheet.end_date}
                  </p>
                </div>
                <div>
                  <label className="font-semibold text-gray-600">Total Hours</label>
                  <p className="mt-1 text-2xl font-bold text-blue-600">{selectedTimesheet.total_hours}</p>
                </div>
                <div>
                  <label className="font-semibold text-gray-600">Number of Entries</label>
                  <p className="mt-1 text-gray-900">{selectedTimesheet.entries?.length || 0} entries</p>
                </div>
              </div>

              {/* Timesheet Grid Template - Same as Form */}
              {(() => {
                // Extract period dates
                const periodStart = selectedTimesheet.period_start || selectedTimesheet.start_date
                const periodEnd = selectedTimesheet.period_end || selectedTimesheet.end_date
                
                if (!periodStart || !periodEnd) {
                  return (
                    <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                      Invalid period dates
                    </div>
                  )
                }

                const startDate = new Date(periodStart)
                const endDate = new Date(periodEnd)
                const year = startDate.getFullYear()
                const month = startDate.getMonth() + 1
                
                // Calculate days in month
                const daysInMonth = new Date(year, month, 0).getDate()
                
                // Helper functions
                const isWeekend = (day: number) => {
                  const date = new Date(year, month - 1, day)
                  const dayOfWeek = date.getDay()
                  return dayOfWeek === 0 || dayOfWeek === 6
                }
                
                const getDayName = (day: number) => {
                  const date = new Date(year, month - 1, day)
                  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                  return dayNames[date.getDay()]
                }
                
                // Build grid data from entries
                const projectMap: { [key: string]: { [day: number]: number } } = {}
                const projectNames: { [key: string]: string } = {}
                
                if (selectedTimesheet.entries && selectedTimesheet.entries.length > 0) {
                  selectedTimesheet.entries.forEach((entry: any) => {
                    try {
                      // Parse entry date - handle both string and date formats
                      let entryDate: Date
                      if (typeof entry.date === 'string') {
                        // Parse YYYY-MM-DD format
                        entryDate = new Date(entry.date + 'T00:00:00') // Add time to avoid timezone issues
                      } else {
                        entryDate = new Date(entry.date)
                      }
                      
                      // Verify the date is in the correct month
                      if (entryDate.getFullYear() !== year || entryDate.getMonth() + 1 !== month) {
                        console.warn(`Entry date ${entry.date} is not in ${year}-${month}`)
                        return
                      }
                      
                      const day = entryDate.getDate()
                      const projectKey = entry.project_id || 'Unknown Project'
                      const projectName = entry.project_name || entry.project_id || 'Unknown Project'
                      
                      if (!projectMap[projectKey]) {
                        projectMap[projectKey] = {}
                        projectNames[projectKey] = projectName
                      }
                      
                      const hours = parseFloat(entry.hours || 0)
                      projectMap[projectKey][day] = (projectMap[projectKey][day] || 0) + hours
                      
                      console.log(`Mapped entry: Project=${projectName}, Day=${day}, Hours=${hours}, Date=${entry.date}`)
                    } catch (error) {
                      console.error(`Error processing entry:`, entry, error)
                    }
                  })
                } else {
                  console.warn('No entries found in timesheet:', selectedTimesheet)
                }
                
                const projects = Object.keys(projectMap)
                
                // Calculate project totals
                const calculateProjectTotal = (projectKey: string) => {
                  return Object.values(projectMap[projectKey] || {}).reduce((sum, hours) => sum + hours, 0)
                }
                
                const grandTotal = projects.reduce((sum, proj) => sum + calculateProjectTotal(proj), 0)
                
                return (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">Timesheet Grid</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="w-full text-xs border-collapse">
                        <thead>
                          <tr className="bg-blue-200 border-b">
                            <th className="border p-2 text-left font-semibold min-w-[150px]">
                              Project \ Grant Name
                            </th>
                            {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => (
                              <th key={day} className={`border p-1 text-center font-semibold w-8 ${
                                isWeekend(day) ? 'bg-gray-300' : ''
                              }`}>
                                <div className="text-[10px] leading-tight">{getDayName(day)}</div>
                                <div className="font-bold">{day}</div>
                              </th>
                            ))}
                            <th className="border p-2 text-center font-semibold bg-blue-300">TOTALS</th>
                            <th className="border p-2 text-center font-semibold bg-blue-300">% of Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {/* Project Rows */}
                          {projects.length > 0 ? (
                            projects.map((projectKey, projectIndex) => {
                              const projectTotal = calculateProjectTotal(projectKey)
                              const percentage = grandTotal > 0 ? ((projectTotal / grandTotal) * 100).toFixed(1) : '0.0'
                              
                              return (
                                <tr key={projectIndex} className="hover:bg-gray-50">
                                  <td className="border p-2 font-medium bg-gray-50">
                                    {projectNames[projectKey]}
                                  </td>
                                  {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
                                    const hours = projectMap[projectKey]?.[day] || 0
                                    return (
                                      <td key={day} className={`border p-2 text-center ${
                                        isWeekend(day) ? 'bg-gray-100' : ''
                                      }`}>
                                        {hours > 0 ? hours.toFixed(2) : ''}
                                      </td>
                                    )
                                  })}
                                  <td className="border p-2 text-center font-semibold bg-gray-100">
                                    {projectTotal.toFixed(2)}
                                  </td>
                                  <td className="border p-2 text-center bg-gray-100">
                                    {percentage}%
                                  </td>
                                </tr>
                              )
                            })
                          ) : (
                            <tr>
                              <td colSpan={daysInMonth + 3} className="border p-4 text-center text-gray-500">
                                No time entries recorded for this timesheet
                              </td>
                            </tr>
                          )}
                          
                          {/* Grand Total Row */}
                          <tr className="bg-blue-50 font-bold">
                            <td className="border p-2 text-right">TOTAL HOURS:</td>
                            {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
                              const dayTotal = projects.reduce((sum, proj) => 
                                sum + (projectMap[proj]?.[day] || 0), 0
                              )
                              return (
                                <td key={day} className={`border p-2 text-center ${
                                  isWeekend(day) ? 'bg-gray-200' : ''
                                }`}>
                                  {dayTotal > 0 ? dayTotal.toFixed(2) : ''}
                                </td>
                              )
                            })}
                            <td className="border p-2 text-center text-lg text-blue-600">
                              {grandTotal.toFixed(2)}
                            </td>
                            <td className="border p-2 text-center">100.0%</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                )
              })()}
              {(selectedTimesheet.status === 'submitted' || selectedTimesheet.status === 'pending') && (
                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    onClick={() => {
                      handleApprove(selectedTimesheet.id)
                      setShowDetailDialog(false)
                    }}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve Timesheet
                  </Button>
                  <Button
                    onClick={() => {
                      handleReject(selectedTimesheet.id)
                      setShowDetailDialog(false)
                    }}
                    variant="outline"
                    className="border-red-300 text-red-700 hover:bg-red-50"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject Timesheet
                  </Button>
                  <Button
                    onClick={() => handleExportPDF(selectedTimesheet.id)}
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

      <TimesheetForm 
        open={showTimesheetForm} 
        onOpenChange={setShowTimesheetForm}
        onSubmitSuccess={loadTimesheets}
      />
    </div>
  )
}
