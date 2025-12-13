"use client";

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  FileText, 
  Plane, 
  Calendar, 
  ClipboardCheck,
  Target 
} from 'lucide-react';

interface ApprovalRequest {
  id: string;
  type: string;
  employee_id: string;
  employee_name?: string;
  submitted_at: string;
  comments?: string;
}

interface ApprovalStats {
  total_pending: number;
  leave_pending: number;
  travel_pending: number;
  timesheet_pending: number;
  performance_pending: number;
}

interface PendingApprovalsWidgetProps {
  employeeId?: string; // Optional, will fetch from current user if not provided
}

const approvalTypeIcons: Record<string, React.ReactNode> = {
  leave: <Calendar className="h-4 w-4" />,
  travel: <Plane className="h-4 w-4" />,
  timesheet: <ClipboardCheck className="h-4 w-4" />,
  performance: <Target className="h-4 w-4" />,
  expense: <FileText className="h-4 w-4" />,
};

const approvalTypeColors: Record<string, string> = {
  leave: 'bg-blue-100 text-blue-800',
  travel: 'bg-purple-100 text-purple-800',
  timesheet: 'bg-green-100 text-green-800',
  performance: 'bg-orange-100 text-orange-800',
  expense: 'bg-yellow-100 text-yellow-800',
};

export function PendingApprovalsWidget({ employeeId }: PendingApprovalsWidgetProps) {
  const [stats, setStats] = useState<ApprovalStats | null>(null);
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchApprovalData();
  }, [employeeId]);

  const fetchApprovalData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Fetch approval stats
      const statsResponse = await fetch('http://localhost:8000/api/v1/approvals/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }
      
      // Fetch pending approvals list
      const approvalsResponse = await fetch('http://localhost:8000/api/v1/approvals/pending', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (approvalsResponse.ok) {
        const approvalsData = await approvalsResponse.json();
        setApprovals(approvalsData.slice(0, 5)); // Show top 5
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching approval data:', err);
      setError('Failed to load approval data');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/approvals/requests/${approvalId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Refresh data
        fetchApprovalData();
      }
    } catch (err) {
      console.error('Error approving request:', err);
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/approvals/requests/${approvalId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        // Refresh data
        fetchApprovalData();
      }
    } catch (err) {
      console.error('Error rejecting request:', err);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Pending Approvals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Pending Approvals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-destructive">
            {error}
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalPending = stats?.total_pending || 0;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Pending Approvals
          {totalPending > 0 && (
            <Badge variant="destructive" className="ml-auto">
              {totalPending}
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Requests awaiting your approval
        </CardDescription>
      </CardHeader>
      <CardContent>
        {totalPending === 0 ? (
          <div className="text-center py-8">
            <CheckCircle2 className="h-12 w-12 mx-auto text-green-500 mb-2" />
            <p className="text-sm text-muted-foreground">
              No pending approvals
            </p>
          </div>
        ) : (
          <>
            {/* Stats Summary */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              {stats && (
                <>
                  {stats.leave_pending > 0 && (
                    <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium">{stats.leave_pending} Leave</span>
                    </div>
                  )}
                  {stats.travel_pending > 0 && (
                    <div className="flex items-center gap-2 p-2 rounded-lg bg-purple-50">
                      <Plane className="h-4 w-4 text-purple-600" />
                      <span className="text-sm font-medium">{stats.travel_pending} Travel</span>
                    </div>
                  )}
                  {stats.timesheet_pending > 0 && (
                    <div className="flex items-center gap-2 p-2 rounded-lg bg-green-50">
                      <ClipboardCheck className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">{stats.timesheet_pending} Timesheet</span>
                    </div>
                  )}
                  {stats.performance_pending > 0 && (
                    <div className="flex items-center gap-2 p-2 rounded-lg bg-orange-50">
                      <Target className="h-4 w-4 text-orange-600" />
                      <span className="text-sm font-medium">{stats.performance_pending} Performance</span>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Recent Approvals List */}
            <div className="space-y-3">
              {approvals.map((approval) => (
                <div
                  key={approval.id}
                  className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    {approvalTypeIcons[approval.type] || <FileText className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge 
                        variant="secondary" 
                        className={approvalTypeColors[approval.type] || 'bg-gray-100 text-gray-800'}
                      >
                        {approval.type.charAt(0).toUpperCase() + approval.type.slice(1)}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(approval.submitted_at)}
                      </span>
                    </div>
                    {approval.comments && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {approval.comments}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-8 w-8 p-0 text-green-600 hover:text-green-700 hover:bg-green-50"
                      onClick={() => handleApprove(approval.id)}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleReject(approval.id)}
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            {totalPending > 5 && (
              <Button variant="outline" className="w-full mt-4">
                View All ({totalPending})
              </Button>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
