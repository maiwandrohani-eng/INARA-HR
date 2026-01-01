
/**
 * Compliance & Legal Page
 */

'use client'
export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PolicyForm } from '@/components/forms/PolicyForm'

export default function CompliancePage() {
  const [showAddPolicy, setShowAddPolicy] = useState(false)
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Compliance & Legal</h1>
          <p className="text-gray-600 mt-2">Policy acknowledgments, training compliance, regulatory tracking</p>
        </div>
        <Button onClick={() => setShowAddPolicy(true)}>
          Add Policy
        </Button>
      </div>

      <PolicyForm 
        open={showAddPolicy} 
        onOpenChange={setShowAddPolicy}
        onSubmitSuccess={() => {
          // Refresh policies list if needed
          setShowAddPolicy(false)
        }}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Policies</CardTitle>
            <CardDescription>Company policies requiring acknowledgment</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">Policy management coming soon...</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Training Compliance</CardTitle>
            <CardDescription>Required training and completion tracking</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">Training compliance tracking coming soon...</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

