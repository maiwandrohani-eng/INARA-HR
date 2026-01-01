/**
 * Benefits Management Page
 * Health insurance, retirement plans, FSA/HSA, etc.
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { BenefitPlanForm } from '@/components/forms/BenefitPlanForm'

export default function BenefitsPage() {
  const [plans, setPlans] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddPlan, setShowAddPlan] = useState(false)

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await apiClient.get('/benefits/plans')
      setPlans(response.data)
    } catch (error) {
      console.error('Failed to fetch benefit plans:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Benefits Management</h1>
          <p className="text-gray-600 mt-2">Manage employee benefits, enrollments, and open enrollment periods</p>
        </div>
        <Button onClick={() => setShowAddPlan(true)}>Add Benefit Plan</Button>
      </div>

      <BenefitPlanForm 
        open={showAddPlan} 
        onOpenChange={setShowAddPlan}
        onSubmitSuccess={fetchPlans}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <Card key={plan.id}>
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.benefit_type}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm"><strong>Provider:</strong> {plan.provider || 'N/A'}</p>
                  <p className="text-sm"><strong>Status:</strong> {plan.is_active ? 'Active' : 'Inactive'}</p>
                  {plan.employee_cost_per_pay_period && (
                    <p className="text-sm"><strong>Employee Cost:</strong> ${plan.employee_cost_per_pay_period}/{plan.currency} per pay period</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

