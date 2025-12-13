'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, FileText, Clock, CheckCircle } from 'lucide-react'
import { GrievanceForm } from '@/components/forms/GrievanceForm'

export default function GrievancePage() {
  const [showGrievanceForm, setShowGrievanceForm] = useState(false)

  const handleFileGrievance = () => {
    setShowGrievanceForm(true)
  }

  const stats = [
    { label: 'Open Grievances', value: '5', icon: FileText, color: 'text-orange-600' },
    { label: 'Under Review', value: '3', icon: Clock, color: 'text-yellow-600' },
    { label: 'Resolved', value: '67', icon: CheckCircle, color: 'text-green-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Grievance Management</h1>
          <p className="text-gray-500 mt-2">Handle employee grievances and disciplinary actions</p>
        </div>
        <Button onClick={handleFileGrievance}>
          <Plus className="w-4 h-4 mr-2" />
          File Grievance
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Grievances</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No grievances filed recently.
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Disciplinary Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No disciplinary actions recorded.
            </div>
          </CardContent>
        </Card>
      </div>

      <GrievanceForm open={showGrievanceForm} onOpenChange={setShowGrievanceForm} />
    </div>
  )
}
