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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Mail, Phone, Calendar, FileText, User, Clock } from 'lucide-react'
import { api } from '@/lib/api-client'
import { InterviewSchedulingDialog } from './InterviewSchedulingDialog'
import { OfferLetterDialog } from './OfferLetterDialog'
import { InterviewFeedbackDialog } from './InterviewFeedbackDialog'

interface Application {
  id: string
  job_posting_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  status: string
  applied_date: string
  resume_url?: string
  cover_letter?: string
  source?: string
}

interface ApplicationListProps {
  jobPostingId?: string
  onStatusUpdate?: () => void
}

export function ApplicationList({ jobPostingId, onStatusUpdate }: ApplicationListProps) {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const [showStatusDialog, setShowStatusDialog] = useState(false)
  const [showInterviewDialog, setShowInterviewDialog] = useState(false)
  const [showOfferDialog, setShowOfferDialog] = useState(false)
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false)
  const [selectedInterviewId, setSelectedInterviewId] = useState<string | null>(null)
  const [interviews, setInterviews] = useState<any[]>([])
  const [loadingInterviews, setLoadingInterviews] = useState(false)
  const [newStatus, setNewStatus] = useState('')
  const [statusNotes, setStatusNotes] = useState('')

  const fetchApplications = async () => {
    try {
      setLoading(true)
      const url = jobPostingId 
        ? `/recruitment/applications?job_posting_id=${jobPostingId}`
        : '/recruitment/applications'
      const data = await api.get(url)
      setApplications(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching applications:', error)
      setApplications([])
    } finally {
      setLoading(false)
    }
  }

  const fetchInterviews = async (applicationId: string) => {
    try {
      setLoadingInterviews(true)
      const data = await api.get(`/recruitment/applications/${applicationId}/interviews`)
      setInterviews(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error fetching interviews:', error)
      setInterviews([])
    } finally {
      setLoadingInterviews(false)
    }
  }

  useEffect(() => {
    fetchApplications()
  }, [jobPostingId])

  useEffect(() => {
    if (selectedApplication) {
      fetchInterviews(selectedApplication.id)
    }
  }, [selectedApplication])

  const handleStatusUpdate = async () => {
    if (!selectedApplication || !newStatus) return

    try {
      await api.patch(`/recruitment/applications/${selectedApplication.id}/status?status=${newStatus}`)
      alert('Application status updated successfully!')
      setShowStatusDialog(false)
      setSelectedApplication(null)
      setNewStatus('')
      setStatusNotes('')
      fetchApplications()
      onStatusUpdate?.()
    } catch (error: any) {
      console.error('Error updating status:', error)
      alert(`Failed to update status: ${error.response?.data?.detail || error.message}`)
    }
  }

  const getStatusBadgeColor = (status: string) => {
    const colors: Record<string, string> = {
      received: 'bg-blue-100 text-blue-800',
      screening: 'bg-yellow-100 text-yellow-800',
      interview: 'bg-purple-100 text-purple-800',
      offer: 'bg-green-100 text-green-800',
      hired: 'bg-emerald-100 text-emerald-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const statusOptions = [
    { value: 'received', label: 'Received' },
    { value: 'screening', label: 'Screening' },
    { value: 'interview', label: 'Interview' },
    { value: 'offer', label: 'Offer' },
    { value: 'hired', label: 'Hired' },
    { value: 'rejected', label: 'Rejected' },
  ]

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Applications</span>
            <Button variant="outline" size="sm" onClick={fetchApplications}>
              Refresh
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading applications...</div>
          ) : applications.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No applications received yet.
            </div>
          ) : (
            <div className="space-y-4">
              {applications.map((app) => (
                <div
                  key={app.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => {
                    setSelectedApplication(app)
                    setShowDetailDialog(true)
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-gray-500" />
                        <h3 className="font-semibold">
                          {app.first_name} {app.last_name}
                        </h3>
                        <Badge className={getStatusBadgeColor(app.status)}>
                          {app.status.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="mt-2 space-y-1 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {app.email}
                        </div>
                        {app.phone && (
                          <div className="flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            {app.phone}
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          Applied: {new Date(app.applied_date).toLocaleDateString()}
                        </div>
                        {app.source && (
                          <div className="text-xs text-gray-500">Source: {app.source}</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Application Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedApplication?.first_name} {selectedApplication?.last_name}
            </DialogTitle>
            <DialogDescription>Application Details</DialogDescription>
          </DialogHeader>

          {selectedApplication && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Email</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Mail className="w-4 h-4" />
                    {selectedApplication.email}
                  </div>
                </div>
                {selectedApplication.phone && (
                  <div>
                    <Label>Phone</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Phone className="w-4 h-4" />
                      {selectedApplication.phone}
                    </div>
                  </div>
                )}
                <div>
                  <Label>Status</Label>
                  <Badge className={`mt-1 ${getStatusBadgeColor(selectedApplication.status)}`}>
                    {selectedApplication.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <Label>Applied Date</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Calendar className="w-4 h-4" />
                    {new Date(selectedApplication.applied_date).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {selectedApplication.cover_letter && (
                <div>
                  <Label>Cover Letter</Label>
                  <div className="mt-1 p-3 bg-gray-50 rounded border text-sm whitespace-pre-wrap">
                    {selectedApplication.cover_letter}
                  </div>
                </div>
              )}

              {selectedApplication.resume_url && (
                <div>
                  <Label>Resume</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-1"
                    onClick={() => window.open(selectedApplication.resume_url, '_blank')}
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    View Resume
                  </Button>
                </div>
              )}

              {/* Interviews Section */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-base font-semibold">Interviews</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowInterviewDialog(true)}
                  >
                    Schedule New
                  </Button>
                </div>
                {loadingInterviews ? (
                  <div className="text-sm text-gray-500">Loading interviews...</div>
                ) : interviews.length === 0 ? (
                  <div className="text-sm text-gray-500">No interviews scheduled yet.</div>
                ) : (
                  <div className="space-y-2">
                    {interviews.map((interview) => (
                      <div key={interview.id} className="border rounded p-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium capitalize">
                                {interview.interview_type}
                              </span>
                              <Badge
                                className={
                                  interview.status === 'completed'
                                    ? 'bg-green-100 text-green-800'
                                    : interview.status === 'scheduled'
                                    ? 'bg-blue-100 text-blue-800'
                                    : 'bg-gray-100 text-gray-800'
                                }
                              >
                                {interview.status.toUpperCase()}
                              </Badge>
                            </div>
                            <div className="text-sm text-gray-600 mt-1">
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                {new Date(interview.scheduled_date).toLocaleDateString()}
                              </div>
                              {interview.rating && (
                                <div className="mt-1">
                                  Rating: {interview.rating}/5
                                </div>
                              )}
                            </div>
                          </div>
                          {interview.status === 'scheduled' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedInterviewId(interview.id)
                                setShowFeedbackDialog(true)
                              }}
                            >
                              Submit Feedback
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-4 border-t">
                <Button
                  onClick={() => {
                    setShowStatusDialog(true)
                    setNewStatus(selectedApplication.status)
                  }}
                >
                  Update Status
                </Button>
                  <Button
                    onClick={() => {
                      setShowStatusDialog(true)
                      setNewStatus(selectedApplication.status)
                    }}
                    variant="outline"
                  >
                    Update Status
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowInterviewDialog(true)
                    }}
                    disabled={selectedApplication.status === 'rejected' || selectedApplication.status === 'hired'}
                  >
                    Schedule Interview
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowOfferDialog(true)
                    }}
                    disabled={selectedApplication.status !== 'interview' && selectedApplication.status !== 'offer'}
                  >
                    Create Offer
                  </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Status Update Dialog */}
      <Dialog open={showStatusDialog} onOpenChange={setShowStatusDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Application Status</DialogTitle>
            <DialogDescription>
              Change the status of {selectedApplication?.first_name} {selectedApplication?.last_name}'s application
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>New Status</Label>
              <Select value={newStatus} onValueChange={setNewStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Notes (Optional)</Label>
              <Textarea
                value={statusNotes}
                onChange={(e) => setStatusNotes(e.target.value)}
                placeholder="Add any notes about this status change..."
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowStatusDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleStatusUpdate}>Update Status</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Interview Scheduling Dialog */}
      {selectedApplication && (
        <InterviewSchedulingDialog
          open={showInterviewDialog}
          onOpenChange={setShowInterviewDialog}
          applicationId={selectedApplication.id}
          applicationName={`${selectedApplication.first_name} ${selectedApplication.last_name}`}
          onSuccess={() => {
            fetchApplications()
            // Update application status to 'interview' after scheduling
            if (selectedApplication.status !== 'interview') {
              // Optionally auto-update status
            }
          }}
        />
      )}

      {/* Offer Letter Dialog */}
      {selectedApplication && (
        <OfferLetterDialog
          open={showOfferDialog}
          onOpenChange={setShowOfferDialog}
          applicationId={selectedApplication.id}
          applicationName={`${selectedApplication.first_name} ${selectedApplication.last_name}`}
          onSuccess={() => {
            fetchApplications()
            // Optionally update application status to 'offer'
            if (selectedApplication.status !== 'offer') {
              // Could auto-update status here
            }
          }}
        />
      )}

      {/* Interview Feedback Dialog */}
      {selectedInterviewId && (
        <InterviewFeedbackDialog
          open={showFeedbackDialog}
          onOpenChange={(open) => {
            setShowFeedbackDialog(open)
            if (!open) {
              setSelectedInterviewId(null)
            }
          }}
          interviewId={selectedInterviewId}
          onSuccess={() => {
            if (selectedApplication) {
              fetchInterviews(selectedApplication.id)
            }
          }}
        />
      )}
    </>
  )
}

