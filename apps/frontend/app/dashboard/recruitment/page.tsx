'use client'

export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Briefcase, Users, CheckCircle, Calendar, MapPin, Building2 } from 'lucide-react'
import { JobPostingForm } from '@/components/forms/JobPostingForm'
import { ApplicationList } from '@/components/recruitment/ApplicationList'
import { api } from '@/lib/api-client'

interface JobPosting {
  id: string
  title: string
  description: string
  employment_type: string
  location?: string
  status: string
  posted_date?: string
  closing_date?: string
  salary_range_min?: string
  salary_range_max?: string
  currency?: string
}

export default function RecruitmentPage() {
  const [showJobForm, setShowJobForm] = useState(false)
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [applicationsCount, setApplicationsCount] = useState(0)
  const [interviewsCount, setInterviewsCount] = useState(0)
  const [selectedJobPostingId, setSelectedJobPostingId] = useState<string | null>(null)

  const fetchJobPostings = async () => {
    try {
      setRefreshing(true)
      const postings = await api.get('/recruitment/')
      setJobPostings(Array.isArray(postings) ? postings : [])
    } catch (error) {
      console.error('Error fetching job postings:', error)
      setJobPostings([])
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const fetchApplicationsCount = async () => {
    try {
      const applications = await api.get('/recruitment/applications')
      const apps = Array.isArray(applications) ? applications : []
      setApplicationsCount(apps.length)
      // Count interviews - would need a separate endpoint or calculate from status
      const interviewStatusApps = apps.filter((app: any) => 
        app.status === 'interview' || app.status === 'offer'
      )
      setInterviewsCount(interviewStatusApps.length)
    } catch (error) {
      console.error('Error fetching application stats:', error)
    }
  }

  useEffect(() => {
    fetchJobPostings()
    fetchApplicationsCount()
  }, [])

  useEffect(() => {
    // Refresh stats when job postings change
    fetchApplicationsCount()
  }, [jobPostings])

  const handleAddJob = () => {
    setShowJobForm(true)
  }

  const handleJobPostingCreated = () => {
    fetchJobPostings()
  }

  const openPostings = jobPostings.filter(p => p.status === 'open' || p.status === 'draft')
  const closedPostings = jobPostings.filter(p => p.status === 'closed' || p.status === 'filled')

  const stats = [
    { 
      label: 'Open Positions', 
      value: openPostings.length.toString(), 
      icon: Briefcase, 
      color: 'text-blue-600' 
    },
    { 
      label: 'Total Applications', 
      value: applicationsCount.toString(), 
      icon: Users, 
      color: 'text-green-600' 
    },
    { 
      label: 'Interviews Scheduled', 
      value: interviewsCount.toString(), 
      icon: CheckCircle, 
      color: 'text-purple-600' 
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Recruitment</h1>
          <p className="text-gray-500 mt-2">Manage job postings and applications</p>
        </div>
        <Button onClick={handleAddJob}>
          <Plus className="w-4 h-4 mr-2" />
          New Job Posting
        </Button>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle>Job Postings</CardTitle>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchJobPostings}
              disabled={refreshing}
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-gray-500">
                Loading job postings...
              </div>
            ) : openPostings.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No active job postings. Create your first posting to start recruiting.
              </div>
            ) : (
              <div className="space-y-4">
                {openPostings.map((posting) => (
                  <div 
                    key={posting.id} 
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-lg">{posting.title}</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            posting.status === 'open' 
                              ? 'bg-green-100 text-green-800' 
                              : posting.status === 'draft'
                              ? 'bg-gray-100 text-gray-800'
                              : posting.status === 'closed'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {posting.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="mt-2 space-y-1 text-sm text-gray-600">
                          {posting.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {posting.location}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Building2 className="w-4 h-4" />
                            {posting.employment_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                          {(posting.salary_range_min || posting.salary_range_max) && (
                            <div>
                              Salary: {posting.currency || 'USD'} {posting.salary_range_min || 'N/A'}
                              {posting.salary_range_max && ` - ${posting.salary_range_max}`}
                            </div>
                          )}
                          {posting.posted_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Posted: {new Date(posting.posted_date).toLocaleDateString()}
                            </div>
                          )}
                          {posting.closing_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Closing: {new Date(posting.closing_date).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                        {posting.description && (
                          <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                            {posting.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="mt-4 flex gap-2">
                      {posting.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="default"
                          onClick={async () => {
                            try {
                              await api.post(`/recruitment/postings/${posting.id}/publish`)
                              alert('Job posting published successfully!')
                              fetchJobPostings()
                            } catch (error: any) {
                              console.error('Error publishing job posting:', error)
                              alert(`Failed to publish: ${error.response?.data?.detail || error.message}`)
                            }
                          }}
                        >
                          Publish Job
                        </Button>
                      )}
                      {posting.status === 'open' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedJobPostingId(posting.id)
                          }}
                        >
                          View Applications
                        </Button>
                      )}
                      {posting.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedJobPostingId(posting.id)
                          }}
                        >
                          View Applications
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          {selectedJobPostingId && (
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">
                  Applications for: {jobPostings.find(p => p.id === selectedJobPostingId)?.title || 'Selected Job'}
                </h3>
                <p className="text-sm text-gray-500">
                  Viewing applications for this specific job posting
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedJobPostingId(null)}
              >
                View All Applications
              </Button>
            </div>
          )}
          <ApplicationList 
            jobPostingId={selectedJobPostingId || undefined}
            onStatusUpdate={fetchApplicationsCount} 
          />
        </div>
      </div>

      <JobPostingForm 
        open={showJobForm} 
        onOpenChange={(open) => {
          setShowJobForm(open)
          if (!open) {
            // Refresh job postings when form closes (in case a new one was created)
            fetchJobPostings()
          }
        }}
      />
    </div>
  )
}
