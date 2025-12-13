'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, TrendingUp, Target, Award, Upload } from 'lucide-react'
import { PerformanceReviewForm } from '@/components/forms/PerformanceReviewForm'
import { exportPerformanceReviewTemplate } from '@/utils/excelExport'

export default function PerformancePage() {
  const [showReviewForm, setShowReviewForm] = useState(false)

  const handleNewReview = () => {
    setShowReviewForm(true)
  }

  const handleExportTemplate = () => {
    exportPerformanceReviewTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to submit performance reviews in bulk.')
  }

  const stats = [
    { label: 'Active Reviews', value: '12', icon: TrendingUp, color: 'text-blue-600' },
    { label: 'Goals Set', value: '156', icon: Target, color: 'text-green-600' },
    { label: 'Completed Reviews', value: '89', icon: Award, color: 'text-purple-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Performance Management</h1>
          <p className="text-gray-500 mt-2">Track employee performance and goals</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportTemplate}>
            <Upload className="w-4 h-4 mr-2" />
            Export Template
          </Button>
          <Button onClick={handleNewReview}>
            <Plus className="w-4 h-4 mr-2" />
            New Review
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
            <CardTitle>Upcoming Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No upcoming performance reviews scheduled.
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Performance Goals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No active goals. Start setting goals for your team.
            </div>
          </CardContent>
        </Card>
      </div>

      <PerformanceReviewForm open={showReviewForm} onOpenChange={setShowReviewForm} />
    </div>
  )
}
