'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp, 
  Target, 
  Sparkles,
  Send,
  Download
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface PerformanceReviewFeedbackFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  reviewId: string | null
  onSuccess?: () => void
}

interface ReviewData {
  id: string
  employee_name: string
  employee: {
    first_name: string
    last_name: string
    position?: { title: string }
  }
  review_period_start: string
  review_period_end: string
  status: string
}

const competencies = [
  { id: 'communication', label: '💬 Communication', description: 'Clarity, listening, and articulation' },
  { id: 'teamwork', label: '🤝 Teamwork & Collaboration', description: 'Working effectively with others' },
  { id: 'technical', label: '🛠️ Technical Skills', description: 'Job-specific expertise and knowledge' },
  { id: 'initiative', label: '🚀 Initiative & Innovation', description: 'Proactive problem-solving' },
  { id: 'leadership', label: '👑 Leadership', description: 'Guiding and inspiring others' },
  { id: 'adaptability', label: '🔄 Adaptability', description: 'Flexibility in changing situations' },
  { id: 'quality', label: '⭐ Quality of Work', description: 'Accuracy, thoroughness, and excellence' },
  { id: 'accountability', label: '✅ Accountability', description: 'Taking ownership and responsibility' },
]

export function PerformanceReviewFeedbackForm({ 
  open, 
  onOpenChange, 
  reviewId,
  onSuccess 
}: PerformanceReviewFeedbackFormProps) {
  const [loading, setLoading] = useState(false)
  const [reviewData, setReviewData] = useState<ReviewData | null>(null)
  const [ratings, setRatings] = useState<Record<string, number>>({})
  const [strengths, setStrengths] = useState('')
  const [areasForImprovement, setAreasForImprovement] = useState('')
  const [developmentPlan, setDevelopmentPlan] = useState('')
  const [overallComments, setOverallComments] = useState('')

  useEffect(() => {
    if (open && reviewId) {
      fetchReviewData()
    }
  }, [open, reviewId])

  const fetchReviewData = async () => {
    if (!reviewId) return
    
    try {
      const response = await apiClient.get(`/performance/reviews`)
      const review = response.data.reviews.find((r: ReviewData) => r.id === reviewId)
      if (review) {
        setReviewData(review)
      }
    } catch (error) {
      console.error('Failed to fetch review data:', error)
    }
  }

  const calculateOverallRating = () => {
    const values = Object.values(ratings)
    if (values.length === 0) return 0
    return Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 10) / 10
  }

  const getOverallRatingLabel = (rating: number) => {
    if (rating >= 4.5) return { label: 'Outstanding', color: 'text-green-600', emoji: '🌟' }
    if (rating >= 4.0) return { label: 'Exceeds Expectations', color: 'text-blue-600', emoji: '⭐' }
    if (rating >= 3.0) return { label: 'Meets Expectations', color: 'text-yellow-600', emoji: '✅' }
    if (rating >= 2.0) return { label: 'Needs Improvement', color: 'text-orange-600', emoji: '⚠️' }
    return { label: 'Below Expectations', color: 'text-red-600', emoji: '❌' }
  }

  const generateAISuggestions = (competency: string, rating: number) => {
    const suggestions: Record<string, Record<string, string>> = {
      communication: {
        low: 'Consider: Active listening workshops, presentation skills training',
        high: 'Strength: Clear communicator. Could mentor others in this area.'
      },
      teamwork: {
        low: 'Focus: Team building activities, collaboration tools training',
        high: 'Strength: Team player. Consider leading cross-functional projects.'
      },
      technical: {
        low: 'Develop: Technical certifications, hands-on workshops, mentorship',
        high: 'Strength: Technical expert. Share knowledge through documentation.'
      },
      leadership: {
        low: 'Growth: Leadership fundamentals course, shadowing senior leaders',
        high: 'Strength: Natural leader. Ready for increased responsibilities.'
      }
    }
    
    const competencySuggestion = suggestions[competency]
    if (!competencySuggestion) return ''
    return rating >= 4 ? competencySuggestion.high : competencySuggestion.low
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!reviewId) return

    setLoading(true)

    try {
      const overallRating = calculateOverallRating()
      
      // Finalize the review with feedback
      await apiClient.post(`/performance/reviews/360/${reviewId}/finalize`, null, {
        params: {
          final_rating: Math.round(overallRating),
          final_strengths: strengths,
          final_areas_for_improvement: areasForImprovement,
          final_development_plan: developmentPlan
        }
      })

      alert('✅ Performance review completed! The employee has been notified.')
      onOpenChange(false)
      if (onSuccess) onSuccess()
    } catch (error) {
      console.error('Error submitting feedback:', error)
      alert('Failed to submit review. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!reviewId) return
    
    try {
      const response = await apiClient.get(`/performance/reviews/360/${reviewId}/export`, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `performance_review_${reviewId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading PDF:', error)
      alert('PDF generation is not yet available for this review. Complete and submit the review first.')
    }
  }

  const overallRating = calculateOverallRating()
  const ratingInfo = getOverallRatingLabel(overallRating)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-600" />
            Performance Review & Feedback
          </DialogTitle>
        </DialogHeader>

        {reviewData && (
          <div className="space-y-6">
            {/* Employee Info Card */}
            <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold">
                    {reviewData.employee.first_name} {reviewData.employee.last_name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {reviewData.employee.position?.title || 'Employee'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Review Period: {new Date(reviewData.review_period_start).toLocaleDateString()} - {new Date(reviewData.review_period_end).toLocaleDateString()}
                  </p>
                </div>
                {overallRating > 0 && (
                  <div className="text-center">
                    <div className={`text-4xl font-bold ${ratingInfo.color}`}>
                      {ratingInfo.emoji} {overallRating}
                    </div>
                    <Badge className="mt-2">{ratingInfo.label}</Badge>
                  </div>
                )}
              </div>
            </Card>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Competency Ratings */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Rate Competencies (1-5)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {competencies.map((competency) => {
                    const rating = ratings[competency.id] || 3
                    const suggestion = generateAISuggestions(competency.id, rating)
                    
                    return (
                      <Card key={competency.id} className="p-4">
                        <div className="space-y-3">
                          <div>
                            <Label className="text-sm font-semibold">{competency.label}</Label>
                            <p className="text-xs text-gray-500">{competency.description}</p>
                          </div>
                          
                          <div className="flex items-center gap-4">
                            <Slider
                              value={[rating]}
                              onValueChange={([value]) => setRatings(prev => ({ ...prev, [competency.id]: value }))}
                              min={1}
                              max={5}
                              step={0.5}
                              className="flex-1"
                            />
                            <div className="text-xl font-bold w-12 text-center">
                              {rating}
                            </div>
                          </div>
                          
                          {suggestion && (
                            <div className="text-xs bg-blue-50 border border-blue-200 rounded p-2">
                              💡 {suggestion}
                            </div>
                          )}
                        </div>
                      </Card>
                    )
                  })}
                </div>
              </div>

              {/* Strengths */}
              <div>
                <Label className="text-lg font-semibold flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Key Strengths & Achievements
                </Label>
                <Textarea
                  value={strengths}
                  onChange={(e) => setStrengths(e.target.value)}
                  placeholder="What are this employee's standout strengths? What have they achieved this period?"
                  rows={4}
                  className="mt-2"
                  required
                />
              </div>

              {/* Areas for Improvement */}
              <div>
                <Label className="text-lg font-semibold flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600" />
                  Areas for Growth & Development
                </Label>
                <Textarea
                  value={areasForImprovement}
                  onChange={(e) => setAreasForImprovement(e.target.value)}
                  placeholder="What skills or behaviors would benefit from development? Be constructive and specific."
                  rows={4}
                  className="mt-2"
                  required
                />
              </div>

              {/* Development Plan */}
              <div>
                <Label className="text-lg font-semibold flex items-center gap-2 mb-2">
                  <Target className="w-5 h-5 text-purple-600" />
                  Development Plan & Next Steps
                </Label>
                <Textarea
                  value={developmentPlan}
                  onChange={(e) => setDevelopmentPlan(e.target.value)}
                  placeholder="What specific actions, training, or goals should they focus on? Include timeline and resources."
                  rows={4}
                  className="mt-2"
                  required
                />
              </div>

              {/* Overall Comments */}
              <div>
                <Label className="text-lg font-semibold mb-2">
                  Additional Comments
                </Label>
                <Textarea
                  value={overallComments}
                  onChange={(e) => setOverallComments(e.target.value)}
                  placeholder="Any additional feedback or context..."
                  rows={3}
                  className="mt-2"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between pt-4 border-t">
                <Button type="button" variant="outline" onClick={handleDownloadPDF}>
                  <Download className="w-4 h-4 mr-2" />
                  Preview PDF
                </Button>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={loading || Object.keys(ratings).length < 3}>
                    <Send className="w-4 h-4 mr-2" />
                    {loading ? 'Submitting...' : 'Complete Review & Notify Employee'}
                  </Button>
                </div>
              </div>
            </form>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
