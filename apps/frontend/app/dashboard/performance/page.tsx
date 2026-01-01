'use client'

export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, TrendingUp, Target, Award, Upload, ClipboardList, Eye, Trash2 } from 'lucide-react'
import { PerformanceReviewForm } from '@/components/forms/PerformanceReviewForm'
import { PerformanceReviewFeedbackForm } from '@/components/forms/PerformanceReviewFeedbackForm'
import { exportPerformanceReviewTemplate } from '@/utils/excelExport'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { useAuthStore } from '@/state/auth.store'

interface PerformanceReview {
  id: string
  employee_name: string
  employee: {
    first_name: string
    last_name: string
  }
  review_period_start: string
  review_period_end: string
  review_type: string
  status: string
  overall_rating?: number
  created_at: string
}

export default function PerformancePage() {
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const [reviews, setReviews] = useState<PerformanceReview[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null)
  const { user } = useAuthStore()
  const isAdmin = user?.roles?.includes('admin') || user?.permissions?.includes('admin:all') || false

  useEffect(() => {
    fetchReviews()
  }, [])

  const fetchReviews = async () => {
    try {
      const token = localStorage.getItem('access_token')
      console.log('🔍 Fetching reviews...')
      console.log('🔑 Token exists:', !!token)
      console.log('🔑 Token value (first 20 chars):', token ? token.substring(0, 20) + '...' : 'NULL')
      
      const response = await apiClient.get('/performance/reviews')
      console.log('✅ Reviews fetched:', response.data)
      setReviews(response.data.reviews || [])
    } catch (error: any) {
      console.error('❌ Failed to fetch reviews:', error)
      console.error('❌ Response data:', error.response?.data)
      console.error('❌ Status:', error.response?.status)
      console.error('❌ Headers sent:', error.config?.headers)
    } finally {
      setLoading(false)
    }
  }

  const handleNewReview = () => {
    setShowReviewForm(true)
  }

  const handleExportTemplate = () => {
    exportPerformanceReviewTemplate()
    alert('Excel template downloaded! Fill it out and use the Import feature to submit performance reviews in bulk.')
  }

  const handleReviewClick = (reviewId: string) => {
    setSelectedReviewId(reviewId)
    setShowFeedbackModal(true)
  }

  const handleFeedbackSuccess = () => {
    fetchReviews() // Refresh the list after feedback submission
  }

  const handleDelete = async (reviewId: string) => {
    if (!confirm('Are you sure you want to delete this performance review? This action cannot be undone.')) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/v1/performance/reviews/360/${reviewId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok || response.status === 204) {
        alert('Performance review deleted successfully')
        fetchReviews()
      } else {
        const errorData = await response.json().catch(() => ({}))
        alert(errorData.detail || 'Failed to delete performance review')
      }
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Failed to delete performance review')
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      in_progress: { label: 'Pending Review', color: 'bg-yellow-100 text-yellow-800' },
      completed: { label: 'Completed', color: 'bg-green-100 text-green-800' },
      draft: { label: 'Draft', color: 'bg-gray-100 text-gray-800' }
    }
    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, color: 'bg-gray-100 text-gray-800' }
    return <Badge className={config.color}>{config.label}</Badge>
  }

  const pendingReviews = reviews.filter(r => r.status === 'in_progress')
  const completedReviews = reviews.filter(r => r.status === 'completed')

  const stats = [
    { label: 'Pending Reviews', value: pendingReviews.length.toString(), icon: ClipboardList, color: 'text-yellow-600' },
    { label: 'Active Reviews', value: reviews.length.toString(), icon: TrendingUp, color: 'text-blue-600' },
    { label: 'Completed Reviews', value: completedReviews.length.toString(), icon: Award, color: 'text-green-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Performance Management</h1>
          <p className="text-gray-500 mt-2">Review and manage team performance</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportTemplate}>
            <Upload className="w-4 h-4 mr-2" />
            Export Template
          </Button>
          <Button onClick={handleNewReview}>
            <Plus className="w-4 h-4 mr-2" />
            New Review
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
          <CardTitle className="flex items-center gap-2">
            <ClipboardList className="w-5 h-5" />
            Submitted Performance Reviews - Awaiting Your Feedback
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : pendingReviews.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No pending reviews. All reviews are up to date!
            </div>
          ) : (
            <div className="space-y-3">
              {pendingReviews.map((review) => (
                <div 
                  key={review.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleReviewClick(review.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-lg">
                          {review.employee?.first_name} {review.employee?.last_name}
                        </h3>
                        {getStatusBadge(review.status)}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        Period: {new Date(review.review_period_start).toLocaleDateString()} - {new Date(review.review_period_end).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        Type: {review.review_type} | Submitted: {new Date(review.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        Review & Provide Feedback
                      </Button>
                      {isAdmin && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(review.id)}
                          className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Completed Reviews</CardTitle>
        </CardHeader>
        <CardContent>
          {completedReviews.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No completed reviews yet.
            </div>
          ) : (
            <div className="space-y-3">
              {completedReviews.map((review) => (
                <div 
                  key={review.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">
                        {review.employee?.first_name} {review.employee?.last_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Rating: {review.overall_rating || 'N/A'} | Completed: {new Date(review.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(review.status)}
                      {isAdmin && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(review.id)}
                          className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <PerformanceReviewForm open={showReviewForm} onOpenChange={setShowReviewForm} onSuccess={fetchReviews} />
      <PerformanceReviewFeedbackForm 
        open={showFeedbackModal} 
        onOpenChange={setShowFeedbackModal} 
        reviewId={selectedReviewId}
        onSuccess={handleFeedbackSuccess}
      />
    </div>
  )
}
