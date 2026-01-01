export const dynamic = "force-dynamic";

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { MapPin, Building2, Calendar, Briefcase, Mail, Phone, FileText } from 'lucide-react'

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
  requirements?: string
  responsibilities?: string
}

export default function CareersPage() {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null)
  const [showJobDetail, setShowJobDetail] = useState(false)
  const [showApplicationForm, setShowApplicationForm] = useState(false)
  
  // Application form state
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [coverLetter, setCoverLetter] = useState('')
  const [resumeUrl, setResumeUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchJobPostings()
  }, [])

  const fetchJobPostings = async () => {
    try {
      setLoading(true)
      // Fetch only open job postings (public endpoint - no auth needed)
      const response = await fetch('http://localhost:8000/api/v1/recruitment/?status=open')
      if (response.ok) {
        const data = await response.json()
        setJobPostings(Array.isArray(data) ? data : [])
      }
    } catch (error) {
      console.error('Error fetching job postings:', error)
      setJobPostings([])
    } finally {
      setLoading(false)
    }
  }

  const handleApply = (job: JobPosting) => {
    setSelectedJob(job)
    setShowApplicationForm(true)
  }

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedJob) return

    setSubmitting(true)
    try {
      const applicationData = {
        job_posting_id: selectedJob.id,
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone || undefined,
        cover_letter: coverLetter || undefined,
        resume_url: resumeUrl || undefined,
        source: 'website',
      }

      const response = await fetch('http://localhost:8000/api/v1/recruitment/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(applicationData),
      })

      if (response.ok) {
        alert('Application submitted successfully! We will review your application and get back to you soon.')
        setShowApplicationForm(false)
        // Reset form
        setFirstName('')
        setLastName('')
        setEmail('')
        setPhone('')
        setCoverLetter('')
        setResumeUrl('')
        setSelectedJob(null)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to submit application')
      }
    } catch (error: any) {
      console.error('Error submitting application:', error)
      alert(`Failed to submit application: ${error.message || 'Unknown error'}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900">Join Our Team</h1>
            <p className="mt-4 text-xl text-gray-600">
              Explore exciting career opportunities at INARA
            </p>
          </div>
        </div>
      </div>

      {/* Job Listings */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading job openings...</p>
          </div>
        ) : jobPostings.length === 0 ? (
          <div className="text-center py-12">
            <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No Open Positions</h3>
            <p className="mt-2 text-gray-500">
              We don't have any open positions at the moment. Please check back later!
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {jobPostings.map((job) => (
              <Card key={job.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-xl">{job.title}</CardTitle>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {job.location && (
                      <Badge variant="outline" className="text-xs">
                        <MapPin className="w-3 h-3 mr-1" />
                        {job.location}
                      </Badge>
                    )}
                    <Badge variant="outline" className="text-xs">
                      <Building2 className="w-3 h-3 mr-1" />
                      {job.employment_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                    {job.description}
                  </p>
                  {(job.salary_range_min || job.salary_range_max) && (
                    <p className="text-sm font-medium text-gray-900 mb-4">
                      {job.currency || 'USD'} {job.salary_range_min || 'N/A'}
                      {job.salary_range_max && ` - ${job.salary_range_max}`}
                    </p>
                  )}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedJob(job)
                        setShowJobDetail(true)
                      }}
                    >
                      View Details
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleApply(job)}
                    >
                      Apply Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Job Detail Dialog */}
      <Dialog open={showJobDetail} onOpenChange={setShowJobDetail}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">{selectedJob?.title}</DialogTitle>
            <DialogDescription>
              {selectedJob?.location && (
                <div className="flex items-center gap-2 mt-2">
                  <MapPin className="w-4 h-4" />
                  {selectedJob.location}
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          {selectedJob && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Employment Type:</span>
                  <p className="text-gray-600">
                    {selectedJob.employment_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                </div>
                {(selectedJob.salary_range_min || selectedJob.salary_range_max) && (
                  <div>
                    <span className="font-medium">Salary Range:</span>
                    <p className="text-gray-600">
                      {selectedJob.currency || 'USD'} {selectedJob.salary_range_min || 'N/A'}
                      {selectedJob.salary_range_max && ` - ${selectedJob.salary_range_max}`}
                    </p>
                  </div>
                )}
                {selectedJob.posted_date && (
                  <div>
                    <span className="font-medium">Posted:</span>
                    <p className="text-gray-600">
                      {new Date(selectedJob.posted_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
                {selectedJob.closing_date && (
                  <div>
                    <span className="font-medium">Closing:</span>
                    <p className="text-gray-600">
                      {new Date(selectedJob.closing_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>

              <div>
                <h3 className="font-semibold mb-2">Job Description</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{selectedJob.description}</p>
              </div>

              {selectedJob.responsibilities && (
                <div>
                  <h3 className="font-semibold mb-2">Responsibilities</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedJob.responsibilities}</p>
                </div>
              )}

              {selectedJob.requirements && (
                <div>
                  <h3 className="font-semibold mb-2">Requirements</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedJob.requirements}</p>
                </div>
              )}

              <div className="flex justify-end pt-4 border-t">
                <Button onClick={() => {
                  setShowJobDetail(false)
                  handleApply(selectedJob)
                }}>
                  Apply for This Position
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Application Form Dialog */}
      <Dialog open={showApplicationForm} onOpenChange={setShowApplicationForm}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Apply for {selectedJob?.title}</DialogTitle>
            <DialogDescription>
              Please fill out the form below to submit your application
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmitApplication} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>First Name *</Label>
                <Input
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label>Last Name *</Label>
                <Input
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <Label>Email *</Label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <Label>Phone</Label>
              <Input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            <div>
              <Label>Resume URL (Optional)</Label>
              <Input
                type="url"
                value={resumeUrl}
                onChange={(e) => setResumeUrl(e.target.value)}
                placeholder="https://..."
              />
              <p className="text-xs text-gray-500 mt-1">
                Link to your resume (Google Drive, Dropbox, LinkedIn, etc.)
              </p>
            </div>

            <div>
              <Label>Cover Letter (Optional)</Label>
              <Textarea
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                rows={6}
                placeholder="Tell us why you're interested in this position and what makes you a great fit..."
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowApplicationForm(false)}
                disabled={submitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Application'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

