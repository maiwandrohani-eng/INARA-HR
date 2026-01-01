/**
 * Succession Planning Page
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { KeyPositionForm } from '@/components/forms/KeyPositionForm'
import { SuccessionPlanForm } from '@/components/forms/SuccessionPlanForm'

export default function SuccessionPage() {
  const [keyPositions, setKeyPositions] = useState<any[]>([])
  const [successionPlans, setSuccessionPlans] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showKeyPositionForm, setShowKeyPositionForm] = useState(false)
  const [showSuccessionPlanForm, setShowSuccessionPlanForm] = useState(false)
  const [selectedKeyPositionId, setSelectedKeyPositionId] = useState<string | undefined>()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [positionsRes, plansRes] = await Promise.all([
        apiClient.get('/succession/key-positions').catch(() => ({ data: [] })),
        apiClient.get('/succession/succession-plans').catch(() => ({ data: [] }))
      ])
      setKeyPositions(positionsRes.data || [])
      setSuccessionPlans(plansRes.data || [])
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
          <h1 className="text-3xl font-bold">Succession Planning</h1>
          <p className="text-gray-600 mt-2">Identify key positions and develop successors</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => {
            setSelectedKeyPositionId(undefined)
            setShowSuccessionPlanForm(true)
          }}>
            Create Succession Plan
          </Button>
          <Button onClick={() => setShowKeyPositionForm(true)}>
            Add Key Position
          </Button>
        </div>
      </div>

      <KeyPositionForm 
        open={showKeyPositionForm} 
        onOpenChange={setShowKeyPositionForm}
        onSubmitSuccess={fetchData}
      />

      <SuccessionPlanForm 
        open={showSuccessionPlanForm} 
        onOpenChange={setShowSuccessionPlanForm}
        keyPositionId={selectedKeyPositionId}
        onSubmitSuccess={fetchData}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : keyPositions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No key positions identified yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {keyPositions.map((position) => (
            <Card key={position.id}>
              <CardHeader>
                <CardTitle>Position ID: {position.position_id}</CardTitle>
                <CardDescription>Criticality: {position.criticality_level}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm"><strong>Has Successor:</strong> {position.has_successor ? 'Yes' : 'No'}</p>
                  <p className="text-sm"><strong>Status:</strong> {position.succession_status}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

