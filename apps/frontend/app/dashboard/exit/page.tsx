export const dynamic = "force-dynamic";

/**
 * Exit Management Page
 */

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ExitInterviewForm } from '@/components/forms/ExitInterviewForm'

export default function ExitManagementPage() {
  const [showExitInterview, setShowExitInterview] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Exit Management</h1>
          <p className="text-gray-600 mt-2">Exit interviews, checklists, and knowledge transfer</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Exit Interviews</CardTitle>
            <CardDescription>Conduct exit interviews</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">Record exit interview responses from departing employees.</p>
            <Button onClick={() => setShowExitInterview(true)} className="w-full">
              Conduct Exit Interview
            </Button>
          </CardContent>
        </Card>
      </div>

      <ExitInterviewForm 
        open={showExitInterview} 
        onOpenChange={setShowExitInterview}
      />
    </div>
  )
}

