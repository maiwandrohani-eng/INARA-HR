
/**
 * Expense Management Page
 */

'use client'
export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { ExpenseReportForm } from '@/components/forms/ExpenseReportForm'

export default function ExpensesPage() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showNewReport, setShowNewReport] = useState(false)

  useEffect(() => {
    // Fetch current user's expense reports
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      // This would need the current user's employee ID
      // For now, just show empty state
      setReports([])
    } catch (error) {
      console.error('Failed to fetch expense reports:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Expense Management</h1>
          <p className="text-gray-600 mt-2">Submit and track expense reports</p>
        </div>
        <Button onClick={() => setShowNewReport(true)}>New Expense Report</Button>
      </div>

      <ExpenseReportForm 
        open={showNewReport} 
        onOpenChange={setShowNewReport}
        onSubmitSuccess={fetchReports}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : reports.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No expense reports yet. Create your first expense report to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <Card key={report.id}>
              <CardHeader>
                <CardTitle>{report.report_number}</CardTitle>
                <CardDescription>{report.report_date}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between">
                  <span className="text-lg font-semibold">${report.total_amount} {report.currency}</span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    report.status === 'approved' ? 'bg-green-100 text-green-800' :
                    report.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {report.status}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

