'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, GraduationCap, BookOpen, Award, Upload } from 'lucide-react'
import { AddCourseForm } from '@/components/forms/AddCourseForm'
import { exportCourseEnrollmentTemplate } from '@/utils/excelExport'

export default function LearningPage() {
  const [showCourseForm, setShowCourseForm] = useState(false)

  const handleAddCourse = () => {
    setShowCourseForm(true)
  }

  const handleExportTemplate = () => {
    exportCourseEnrollmentTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to enroll employees in courses in bulk.')
  }

  const stats = [
    { label: 'Active Courses', value: '24', icon: BookOpen, color: 'text-blue-600' },
    { label: 'Total Enrollments', value: '156', icon: GraduationCap, color: 'text-green-600' },
    { label: 'Certificates Issued', value: '89', icon: Award, color: 'text-purple-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Learning & Development</h1>
          <p className="text-gray-500 mt-2">Manage training courses and certifications</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportTemplate}>
            <Upload className="w-4 h-4 mr-2" />
            Export Template
          </Button>
          <Button onClick={handleAddCourse}>
            <Plus className="w-4 h-4 mr-2" />
            Add Course
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

      <Card>
        <CardHeader>
          <CardTitle>Training Courses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Course</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Enrollments</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No training courses available. Add your first course to get started.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <AddCourseForm open={showCourseForm} onOpenChange={setShowCourseForm} />
    </div>
  )
}
