'use client'

export const dynamic = "force-dynamic";

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DollarSign, TrendingUp, Users, Upload } from 'lucide-react'
import { PayrollForm } from '@/components/forms/PayrollForm'
import { exportPayrollTemplate } from '@/utils/excelExport'

export default function CompensationPage() {
  const [showPayrollForm, setShowPayrollForm] = useState(false)

  const handleProcessPayroll = () => {
    setShowPayrollForm(true)
  }

  const handleExportTemplate = () => {
    exportPayrollTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to process payroll in bulk.')
  }

  const stats = [
    { label: 'Total Payroll', value: '$456,789', icon: DollarSign, color: 'text-green-600' },
    { label: 'Average Salary', value: '$52,340', icon: TrendingUp, color: 'text-blue-600' },
    { label: 'Salary Reviews Due', value: '8', icon: Users, color: 'text-orange-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compensation & Payroll</h1>
          <p className="text-gray-500 mt-2">Manage salaries, benefits, and payroll</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportTemplate}>
            <Upload className="w-4 h-4 mr-2" />
            Export Template
          </Button>
          <Button onClick={handleProcessPayroll}>
            <DollarSign className="w-4 h-4 mr-2" />
            Process Payroll
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Salary Bands</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No salary bands configured. Set up salary structures for your organization.
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Salary Changes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No recent salary changes recorded.
            </div>
          </CardContent>
        </Card>
      </div>

      <PayrollForm open={showPayrollForm} onOpenChange={setShowPayrollForm} />
    </div>
  )
}
