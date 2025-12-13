'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, CheckCircle, XCircle, Eye } from 'lucide-react';
import { payrollService, Payroll } from '@/services/payroll.service';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';

interface ApprovalQueueProps {
  userRole: string;
  onRefresh: () => void;
}

export default function ApprovalQueue({ userRole, onRefresh }: ApprovalQueueProps) {
  const { toast } = useToast();
  const router = useRouter();
  const [payrolls, setPayrolls] = useState<Payroll[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [selectedPayroll, setSelectedPayroll] = useState<Payroll | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'approve' | 'reject'>('approve');
  const [comments, setComments] = useState('');

  useEffect(() => {
    loadPendingPayrolls();
  }, [userRole]);

  const loadPendingPayrolls = async () => {
    try {
      setLoading(true);
      // Determine which status to filter by based on user role
      let statusFilter: string | undefined;
      if (userRole === 'finance_manager') {
        statusFilter = 'PENDING_FINANCE';
      } else if (userRole === 'ceo' || userRole === 'admin') {
        statusFilter = 'PENDING_CEO';
      }

      const data = await payrollService.listPayrolls({
        page: 1,
        page_size: 50,
        status: statusFilter,
      });
      setPayrolls(data.payrolls);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load pending payrolls',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const openDialog = (payroll: Payroll, type: 'approve' | 'reject') => {
    setSelectedPayroll(payroll);
    setDialogType(type);
    setComments('');
    setShowDialog(true);
  };

  const handleApprove = async () => {
    if (!selectedPayroll) return;

    try {
      setActionLoading(true);
      
      if (userRole === 'finance_manager') {
        await payrollService.financeApprove(
          selectedPayroll.id,
          true,
          comments || undefined
        );
        toast({
          title: 'Success',
          description: 'Payroll approved and forwarded to CEO',
        });
      } else if (userRole === 'ceo' || userRole === 'admin') {
        await payrollService.ceoApprove(
          selectedPayroll.id,
          true,
          comments || undefined
        );
        toast({
          title: 'Success',
          description: 'Payroll approved. Ready for processing.',
        });
      }

      setShowDialog(false);
      loadPendingPayrolls();
      onRefresh();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to approve payroll',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedPayroll) return;
    if (!comments.trim()) {
      toast({
        title: 'Error',
        description: 'Please provide a reason for rejection',
        variant: 'destructive',
      });
      return;
    }

    try {
      setActionLoading(true);

      if (userRole === 'finance_manager') {
        await payrollService.financeApprove(
          selectedPayroll.id,
          false,
          comments
        );
        toast({
          title: 'Rejected',
          description: 'Payroll rejected and sent back to HR',
        });
      } else if (userRole === 'ceo' || userRole === 'admin') {
        await payrollService.ceoApprove(
          selectedPayroll.id,
          false,
          comments
        );
        toast({
          title: 'Rejected',
          description: 'Payroll rejected and sent back to HR',
        });
      }

      setShowDialog(false);
      loadPendingPayrolls();
      onRefresh();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to reject payroll',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  const roleTitle = userRole === 'finance_manager' 
    ? 'Finance Manager Approval Queue'
    : 'CEO Approval Queue';

  if (payrolls.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{roleTitle}</CardTitle>
          <CardDescription>No pending approvals</CardDescription>
        </CardHeader>
        <CardContent className="text-center py-12 text-muted-foreground">
          <p>You have no payrolls awaiting your approval</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{roleTitle}</CardTitle>
          <CardDescription>
            {payrolls.length} payroll{payrolls.length !== 1 ? 's' : ''} awaiting your review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Period</TableHead>
                  <TableHead>Payment Date</TableHead>
                  <TableHead>Employees</TableHead>
                  <TableHead className="text-right">Total Amount</TableHead>
                  <TableHead>Created By</TableHead>
                  <TableHead>Created Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payrolls.map((payroll) => (
                  <TableRow key={payroll.id}>
                    <TableCell className="font-medium">
                      {format(new Date(payroll.year, payroll.month - 1), 'MMMM yyyy')}
                    </TableCell>
                    <TableCell>
                      {format(new Date(payroll.payment_date), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell>{payroll.entries.length} employees</TableCell>
                    <TableCell className="text-right font-semibold">
                      ${parseFloat(payroll.total_net_salary.toString()).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {payroll.created_by_id || 'Unknown'}
                    </TableCell>
                    <TableCell>
                      {format(new Date(payroll.created_at), 'MMM dd, yyyy')}
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/dashboard/payroll/${payroll.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => openDialog(payroll, 'approve')}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Approve
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => openDialog(payroll, 'reject')}
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogType === 'approve' ? 'Approve Payroll' : 'Reject Payroll'}
            </DialogTitle>
            <DialogDescription>
              {selectedPayroll && (
                <>
                  <div className="space-y-2 mt-4">
                    <div className="flex justify-between">
                      <span className="font-semibold">Period:</span>
                      <span>
                        {format(
                          new Date(selectedPayroll.year, selectedPayroll.month - 1),
                          'MMMM yyyy'
                        )}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold">Total Amount:</span>
                      <span>
                        ${parseFloat(selectedPayroll.total_net_salary.toString()).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-semibold">Employees:</span>
                      <span>{selectedPayroll.entries.length}</span>
                    </div>
                  </div>
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">
                Comments {dialogType === 'reject' && <span className="text-red-600">*</span>}
              </label>
              <Textarea
                placeholder={
                  dialogType === 'approve'
                    ? 'Optional comments...'
                    : 'Please provide reason for rejection...'
                }
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={4}
                className="mt-1"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDialog(false)}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            {dialogType === 'approve' ? (
              <Button onClick={handleApprove} disabled={actionLoading}>
                {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Approve
              </Button>
            ) : (
              <Button
                variant="destructive"
                onClick={handleReject}
                disabled={actionLoading}
              >
                {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Reject
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
