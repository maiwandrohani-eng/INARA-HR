
/**
 * Workforce Planning Page
 */

'use client'
export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { PositionRequisitionForm } from '@/components/forms/PositionRequisitionForm'
import { WorkforcePlanForm } from '@/components/forms/WorkforcePlanForm'

export default function WorkforcePage() {
  const [requisitions, setRequisitions] = useState<any[]>([])
  const [plans, setPlans] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showRequisitionForm, setShowRequisitionForm] = useState(false)
  const [showPlanForm, setShowPlanForm] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [requisitionsRes, plansRes] = await Promise.all([
        apiClient.get('/workforce/requisitions').catch(() => ({ data: [] })),
        apiClient.get('/workforce/plans').catch(() => ({ data: [] }))
      ])
      setRequisitions(requisitionsRes.data || [])
      setPlans(plansRes.data || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Workforce Planning</h1>
          <p className="text-gray-600 mt-2">Headcount forecasting, budget planning, position requisitions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowPlanForm(true)}>
            Create Workforce Plan
          </Button>
          <Button onClick={() => setShowRequisitionForm(true)}>
            New Requisition
          </Button>
        </div>
      </div>

      <WorkforcePlanForm 
        open={showPlanForm} 
        onOpenChange={setShowPlanForm}
        onSubmitSuccess={fetchData}
      />

      <PositionRequisitionForm 
        open={showRequisitionForm} 
        onOpenChange={setShowRequisitionForm}
        onSubmitSuccess={fetchData}
      />

      {plans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Workforce Plans</CardTitle>
            <CardDescription>Strategic workforce planning documents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {plans.map((plan) => (
                <div key={plan.id} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">{plan.plan_name}</p>
                      <p className="text-sm text-gray-500">Year: {plan.plan_year}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(plan.plan_start_date).toLocaleDateString()} - {new Date(plan.plan_end_date).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      plan.status === 'approved' ? 'bg-green-100 text-green-800' :
                      plan.status === 'active' ? 'bg-blue-100 text-blue-800' :
                      plan.status === 'archived' ? 'bg-gray-100 text-gray-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {plan.status}
                    </span>
                  </div>
                  {plan.total_budget && (
                    <p className="text-sm text-gray-600 mt-2">
                      Budget: {plan.currency} {parseFloat(plan.total_budget).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Position Requisitions</CardTitle>
          <CardDescription>Open and pending position requests</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading...</p>
          ) : requisitions.length === 0 ? (
            <p className="text-gray-500">No requisitions yet.</p>
          ) : (
            <div className="space-y-4">
              {requisitions.map((req) => (
                <div key={req.id} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold">{req.job_title}</p>
                      <p className="text-sm text-gray-500">{req.requisition_number}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      req.status === 'approved' ? 'bg-green-100 text-green-800' :
                      req.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {req.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

