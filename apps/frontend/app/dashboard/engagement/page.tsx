/**
 * Employee Engagement Page
 */

'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { SurveyForm } from '@/components/forms/SurveyForm'
import { RecognitionForm } from '@/components/forms/RecognitionForm'

export default function EngagementPage() {
  const [surveys, setSurveys] = useState<any[]>([])
  const [recognitions, setRecognitions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showSurveyForm, setShowSurveyForm] = useState(false)
  const [showRecognitionForm, setShowRecognitionForm] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [surveysRes, recognitionsRes] = await Promise.all([
        apiClient.get('/engagement/surveys'),
        apiClient.get('/engagement/recognitions')
      ])
      setSurveys(surveysRes.data)
      setRecognitions(recognitionsRes.data)
    } catch (error) {
      console.error('Failed to fetch engagement data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Employee Engagement</h1>
          <p className="text-gray-600 mt-2">Surveys, recognition, and feedback</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowSurveyForm(true)}>
            Create Survey
          </Button>
          <Button onClick={() => setShowRecognitionForm(true)}>
            Recognize Employee
          </Button>
        </div>
      </div>

      <SurveyForm 
        open={showSurveyForm} 
        onOpenChange={setShowSurveyForm}
        onSubmitSuccess={fetchData}
      />

      <RecognitionForm 
        open={showRecognitionForm} 
        onOpenChange={setShowRecognitionForm}
        onSubmitSuccess={fetchData}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Surveys</CardTitle>
            <CardDescription>Employee engagement surveys</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : surveys.length === 0 ? (
              <p className="text-gray-500">No surveys yet.</p>
            ) : (
              <div className="space-y-2">
                {surveys.map((survey) => (
                  <div key={survey.id} className="p-3 border rounded">
                    <p className="font-medium">{survey.title}</p>
                    <p className="text-sm text-gray-500">{survey.response_count} responses</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recognitions</CardTitle>
            <CardDescription>Employee recognition and awards</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : recognitions.length === 0 ? (
              <p className="text-gray-500">No recognitions yet.</p>
            ) : (
              <div className="space-y-2">
                {recognitions.slice(0, 5).map((recognition) => (
                  <div key={recognition.id} className="p-3 border rounded">
                    <p className="font-medium">{recognition.title}</p>
                    <p className="text-sm text-gray-500">{recognition.recognition_date}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

