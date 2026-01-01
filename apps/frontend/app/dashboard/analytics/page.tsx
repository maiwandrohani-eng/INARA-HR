export const dynamic = "force-dynamic";

'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BarChart3, TrendingUp, Users, Calendar } from 'lucide-react'
import { GenerateReportForm } from '@/components/forms/GenerateReportForm'

export default function AnalyticsPage() {
  const [showReportForm, setShowReportForm] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics & Reports</h1>
          <p className="text-gray-500 mt-2">View HR metrics and generate reports</p>
        </div>
        <Button onClick={() => setShowReportForm(true)}>
          <BarChart3 className="w-4 h-4 mr-2" />
          Generate Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Headcount</p>
                <p className="text-3xl font-bold mt-2">245</p>
                <p className="text-sm text-green-600 mt-1">+12% from last month</p>
              </div>
              <Users className="w-12 h-12 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Turnover Rate</p>
                <p className="text-3xl font-bold mt-2">8.5%</p>
                <p className="text-sm text-red-600 mt-1">+1.2% from last month</p>
              </div>
              <TrendingUp className="w-12 h-12 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg. Leave Days</p>
                <p className="text-3xl font-bold mt-2">12.4</p>
                <p className="text-sm text-gray-500 mt-1">Per employee</p>
              </div>
              <Calendar className="w-12 h-12 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Time to Hire</p>
                <p className="text-3xl font-bold mt-2">28</p>
                <p className="text-sm text-gray-500 mt-1">Days average</p>
              </div>
              <BarChart3 className="w-12 h-12 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Department Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center">
            <p className="text-gray-500">Chart visualization coming soon</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Headcount Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-64 flex items-center justify-center">
            <p className="text-gray-500">Chart visualization coming soon</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Available Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20">
              <div className="text-center">
                <Users className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Employee Directory</span>
              </div>
            </Button>
            <Button variant="outline" className="h-20">
              <div className="text-center">
                <Calendar className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Leave Summary</span>
              </div>
            </Button>
            <Button variant="outline" className="h-20">
              <div className="text-center">
                <BarChart3 className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Performance Report</span>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>

      <GenerateReportForm open={showReportForm} onOpenChange={setShowReportForm} />
    </div>
  )
}
