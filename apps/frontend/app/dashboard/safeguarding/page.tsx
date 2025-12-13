'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Shield, AlertTriangle, Clock, CheckCircle } from 'lucide-react'
import { SafeguardingReportForm } from '@/components/forms/SafeguardingReportForm'

export default function SafeguardingPage() {
  const [showReportForm, setShowReportForm] = useState(false)

  const handleReportCase = () => {
    setShowReportForm(true)
  }

  const stats = [
    { label: 'Open Cases', value: '3', icon: AlertTriangle, color: 'text-red-600' },
    { label: 'Under Investigation', value: '2', icon: Shield, color: 'text-yellow-600' },
    { label: 'Resolved Cases', value: '45', icon: CheckCircle, color: 'text-green-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Safeguarding</h1>
          <p className="text-gray-500 mt-2">Manage safeguarding cases and investigations</p>
        </div>
        <Button onClick={handleReportCase}>
          <Plus className="w-4 h-4 mr-2" />
          Report Case
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
          <CardTitle>Active Safeguarding Cases</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Case Number</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No active safeguarding cases.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <SafeguardingReportForm open={showReportForm} onOpenChange={setShowReportForm} />
    </div>
  )
}
