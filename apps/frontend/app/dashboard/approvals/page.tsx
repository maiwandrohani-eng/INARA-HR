'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { CheckCircle, XCircle, Clock, FileText, Calendar, Plane, ClockIcon } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface ApprovalRequest {
  id: string
  request_type: 'leave' | 'travel' | 'timesheet' | 'expense' | 'performance'
  request_id: string
  employee_id: string
  employee_name?: string
  status: 'pending' | 'approved' | 'rejected' | 'cancelled'
  comments?: string
  submitted_at: string
  reviewed_at?: string
  approver_id: string
}

export default function ApprovalsPage() {
  const { toast } = useToast()
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null)
  const [showActionDialog, setShowActionDialog] = useState(false)
  const [action, setAction] = useState<'approve' | 'reject' | null>(null)
  const [comments, setComments] = useState('')

  useEffect(() => {
    fetchPendingApprovals()
  }, [])

  const fetchPendingApprovals = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/approvals/pending')
      setApprovals(response.data || [])
    } catch (error: any) {
      console.error('Failed to fetch approvals:', error)
      if (error.response?.status === 403) {
        toast({
          title: 'Access Denied',
          description: 'You do not have permission to view approvals',
          variant: 'destructive',
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleAction = (approval: ApprovalRequest, actionType: 'approve' | 'reject') => {
    setSelectedApproval(approval)
    setAction(actionType)
    setComments('')
    setShowActionDialog(true)
  }

  const submitAction = async () => {
    if (!selectedApproval) return

    try {
      const endpoint = action === 'approve' 
        ? `/approvals/requests/${selectedApproval.id}/approve`
        : `/approvals/requests/${selectedApproval.id}/reject`
      
      // Send comments as query parameter
      const url = comments 
        ? `${endpoint}?comments=${encodeURIComponent(comments)}`
        : endpoint
      
      await apiClient.post(url)
      
      toast({
        title: 'Success',
        description: `Request ${action === 'approve' ? 'approved' : 'rejected'} successfully`,
      })
      
      setShowActionDialog(false)
      setSelectedApproval(null)
      setAction(null)
      setComments('')
      fetchPendingApprovals()
    } catch (error: any) {
      console.error(`Failed to ${action} request:`, error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || `Failed to ${action} request`,
        variant: 'destructive',
      })
    }
  }

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'leave':
        return <Calendar className="h-5 w-5" />
      case 'travel':
        return <Plane className="h-5 w-5" />
      case 'timesheet':
        return <ClockIcon className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getRequestTypeLabel = (type: string) => {
    switch (type) {
      case 'leave':
        return 'Leave Request'
      case 'travel':
        return 'Travel Request'
      case 'timesheet':
        return 'Timesheet'
      case 'expense':
        return 'Expense Report'
      case 'performance':
        return 'Performance Review'
      default:
        return type
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Pending Approvals</h1>
          <p className="text-gray-600 mt-2">Review and approve requests from your team</p>
        </div>
        <div className="text-center py-12">
          <p className="text-gray-500">Loading approvals...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Pending Approvals</h1>
        <p className="text-gray-600 mt-2">Review and approve requests from your team</p>
      </div>

      {approvals.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No pending approvals</p>
            <p className="text-gray-400 text-sm mt-2">You're all caught up!</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((approval) => (
            <Card key={approval.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    {getRequestTypeIcon(approval.request_type)}
                    <div>
                      <CardTitle className="text-lg">
                        {getRequestTypeLabel(approval.request_type)}
                      </CardTitle>
                      <CardDescription>
                        Submitted by {approval.employee_name || 'Employee'}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-yellow-50 text-yellow-800 border-yellow-200">
                    {approval.status.toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Submitted</p>
                      <p className="font-medium">
                        {new Date(approval.submitted_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Request ID</p>
                      <p className="font-mono text-xs">{approval.request_id.slice(0, 8)}...</p>
                    </div>
                  </div>

                  {approval.comments && (
                    <div>
                      <p className="text-gray-500 text-sm mb-1">Comments</p>
                      <p className="text-sm">{approval.comments}</p>
                    </div>
                  )}

                  <div className="flex gap-2 pt-2 border-t">
                    <Button
                      size="sm"
                      onClick={() => handleAction(approval, 'approve')}
                      className="flex-1"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleAction(approval, 'reject')}
                      className="flex-1"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={showActionDialog} onOpenChange={setShowActionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {action === 'approve' ? 'Approve Request' : 'Reject Request'}
            </DialogTitle>
            <DialogDescription>
              {action === 'approve' 
                ? 'Add optional comments and confirm approval'
                : 'Provide a reason for rejection (required)'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="comments">
                Comments {action === 'reject' && '*'}
              </Label>
              <Textarea
                id="comments"
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder={action === 'approve' 
                  ? 'Optional comments...'
                  : 'Reason for rejection...'}
                rows={4}
                required={action === 'reject'}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowActionDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={submitAction}
              variant={action === 'reject' ? 'destructive' : 'default'}
              disabled={action === 'reject' && !comments.trim()}
            >
              Confirm {action === 'approve' ? 'Approval' : 'Rejection'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

