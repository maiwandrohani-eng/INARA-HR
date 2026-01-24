'use client'

import { useState } from 'react'
import { API_BASE_URL } from '@/lib/api-config'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Calendar, FileText, Download } from 'lucide-react'
import { Input } from '@/components/ui/input'

interface GenerateReportFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function GenerateReportForm({ open, onOpenChange }: GenerateReportFormProps) {
  const [loading, setLoading] = useState(false)
  
  const [reportType, setReportType] = useState('')
  const [format, setFormat] = useState('pdf')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [includeInactive, setIncludeInactive] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const reportParams = new URLSearchParams({
        report_type: reportType,
        format: format,
        start_date: startDate,
        end_date: endDate,
        include_inactive: includeInactive.toString(),
      })

      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_BASE_URL}/reports/generate?${reportParams}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to generate report')
      }

      // Download the report
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const timestamp = new Date().toISOString().split('T')[0]
      a.download = `${reportType}_report_${timestamp}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      alert('Report generated and downloaded successfully!')
      onOpenChange(false)
      resetForm()
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setReportType('')
    setFormat('pdf')
    setStartDate('')
    setEndDate('')
    setIncludeInactive(false)
  }

  const getReportDescription = () => {
    switch (reportType) {
      case 'employee_directory':
        return 'Complete list of all employees with contact information and employment details'
      case 'leave_summary':
        return 'Summary of leave requests, balances, and usage by employee'
      case 'performance_report':
        return 'Performance review data and ratings for the selected period'
      case 'payroll_summary':
        return 'Payroll processing summary including salaries, deductions, and net pay'
      case 'turnover_analysis':
        return 'Employee turnover statistics and trends'
      case 'recruitment_metrics':
        return 'Hiring statistics including time-to-hire and source effectiveness'
      case 'training_completion':
        return 'Training course completions and certification status'
      case 'grievance_log':
        return 'Log of all grievances filed and their resolution status'
      default:
        return 'Select a report type to see its description'
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Generate HR Report
          </DialogTitle>
          <DialogDescription>
            Generate and download comprehensive HR reports
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Report Type */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="report-type">Report Type *</Label>
              <Select value={reportType} onValueChange={setReportType} required>
                <SelectTrigger id="report-type">
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="employee_directory">Employee Directory</SelectItem>
                  <SelectItem value="leave_summary">Leave Summary</SelectItem>
                  <SelectItem value="performance_report">Performance Report</SelectItem>
                  <SelectItem value="payroll_summary">Payroll Summary</SelectItem>
                  <SelectItem value="turnover_analysis">Turnover Analysis</SelectItem>
                  <SelectItem value="recruitment_metrics">Recruitment Metrics</SelectItem>
                  <SelectItem value="training_completion">Training Completion</SelectItem>
                  <SelectItem value="grievance_log">Grievance Log</SelectItem>
                  <SelectItem value="headcount_report">Headcount Report</SelectItem>
                  <SelectItem value="demographic_analysis">Demographic Analysis</SelectItem>
                </SelectContent>
              </Select>
              {reportType && (
                <p className="text-sm text-gray-600 mt-2">
                  {getReportDescription()}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="format">Export Format *</Label>
              <Select value={format} onValueChange={setFormat} required>
                <SelectTrigger id="format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF Document</SelectItem>
                  <SelectItem value="excel">Excel Spreadsheet</SelectItem>
                  <SelectItem value="csv">CSV File</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Date Range */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Date Range (Optional)</h3>
            <p className="text-xs text-gray-500">
              Leave blank for all-time data. Date range is applicable for time-based reports.
            </p>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Start Date
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="end-date" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  End Date
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                />
              </div>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold">Report Options</h3>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="include-inactive"
                checked={includeInactive}
                onChange={(e) => setIncludeInactive(e.target.checked)}
                className="rounded border-gray-300"
              />
              <Label htmlFor="include-inactive" className="text-sm font-normal cursor-pointer">
                Include inactive/terminated employees
              </Label>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Reports are generated in real-time based on current data. 
              Large reports may take a few moments to generate.
            </p>
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || !reportType}
              className="bg-gradient-to-r from-pink-600 to-cyan-600 hover:from-pink-700 hover:to-cyan-700"
            >
              <Download className="w-4 h-4 mr-2" />
              {loading ? 'Generating...' : 'Generate & Download'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
