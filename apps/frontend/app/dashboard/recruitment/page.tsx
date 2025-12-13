'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Briefcase, Users, CheckCircle } from 'lucide-react'
import { JobPostingForm } from '@/components/forms/JobPostingForm'

export default function RecruitmentPage() {
  const [showJobForm, setShowJobForm] = useState(false)

  const handleAddJob = () => {
    setShowJobForm(true)
  }

  const stats = [
    { label: 'Open Positions', value: '6', icon: Briefcase, color: 'text-blue-600' },
    { label: 'Total Applications', value: '42', icon: Users, color: 'text-green-600' },
    { label: 'Interviews Scheduled', value: '12', icon: CheckCircle, color: 'text-purple-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Recruitment</h1>
          <p className="text-gray-500 mt-2">Manage job postings and applications</p>
        </div>
        <Button onClick={handleAddJob}>
          <Plus className="w-4 h-4 mr-2" />
          New Job Posting
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
            <CardTitle>Open Job Postings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No active job postings. Create your first posting to start recruiting.
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-gray-500">
              No applications received yet.
            </div>
          </CardContent>
        </Card>
      </div>

      <JobPostingForm open={showJobForm} onOpenChange={setShowJobForm} />
    </div>
  )
}
