'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Clock, CheckCircle, AlertCircle, Download } from 'lucide-react'
import { TimesheetForm } from '@/components/forms/TimesheetForm'
import { timesheetService, type Timesheet } from '@/services/timesheet.service'

export default function TimesheetsPage() {
  const [showTimesheetForm, setShowTimesheetForm] = useState(false)
  const [timesheets, setTimesheets] = useState<Timesheet[]>([])
  const [loading, setLoading] = useState(true)

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
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportPDF(timesheet.id)}
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Export
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

      <TimesheetForm open={showTimesheetForm} onOpenChange={setShowTimesheetForm} />
    </div>
  )
}
