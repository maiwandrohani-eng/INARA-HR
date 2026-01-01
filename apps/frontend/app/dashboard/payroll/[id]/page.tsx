'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
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
import { Loader2, ArrowLeft, Download, Send, CheckCircle, XCircle } from 'lucide-react';
import { payrollService, Payroll } from '@/services/payroll.service';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';
import { useAuthStore } from '@/state/auth.store';

const statusColors = {
  DRAFT: 'bg-gray-500',
  PENDING_FINANCE: 'bg-yellow-500',
  PENDING_CEO: 'bg-orange-500',
  APPROVED: 'bg-green-500',
  REJECTED: 'bg-red-500',
  PROCESSED: 'bg-blue-500',
};

const statusLabels = {
  DRAFT: 'Draft',
  PENDING_FINANCE: 'Pending Finance',
  PENDING_CEO: 'Pending CEO',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  PROCESSED: 'Processed',
};

export default function PayrollDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const { user } = useAuthStore();
  const [payroll, setPayroll] = useState<Payroll | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (params.id) {
      loadPayroll();
    }
  }, [params.id]);

  const loadPayroll = async () => {
    try {
      setLoading(true);
      const data = await payrollService.getPayroll(params.id as string);
      setPayroll(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load payroll details',
        variant: 'destructive',
      });
      router.push('/dashboard/payroll');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitToFinance = async () => {
    if (!payroll) return;
    
    try {
      setActionLoading(true);
      await payrollService.submitToFinance(payroll.id);
      toast({
        title: 'Success',
        description: 'Payroll submitted to Finance for review',
      });
      loadPayroll();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to submit payroll',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!payroll) return;
    
    try {
      setActionLoading(true);
      const token = localStorage.getItem('access_token');
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${baseUrl}/payroll/${payroll.id}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `payroll_${payroll.year}_${String(payroll.month).padStart(2, '0')}_payslips.zip`;
      
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: 'Success',
        description: 'Payslips downloaded successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to download payslips',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  if (!payroll) {
    return null;
  }

  const userRole = user?.roles?.[0] || 'employee';
  const canSubmit = payroll.status === 'DRAFT' && (userRole === 'hr_manager' || userRole === 'admin');
  const canDownload = (payroll.status === 'APPROVED' || payroll.status === 'PROCESSED');

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.push('/dashboard/payroll')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              Payroll - {format(new Date(payroll.year, payroll.month - 1), 'MMMM yyyy')}
            </h1>
            <p className="text-muted-foreground">
              Payment Date: {format(new Date(payroll.payment_date), 'MMMM dd, yyyy')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={statusColors[payroll.status]}>
            {statusLabels[payroll.status]}
          </Badge>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Employees
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{payroll.entries.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Basic
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${parseFloat(payroll.total_basic_salary.toString()).toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Gross
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${parseFloat(payroll.total_gross_salary.toString()).toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Net
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${parseFloat(payroll.total_net_salary.toString()).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      {(canSubmit || canDownload) && (
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent className="flex gap-2">
            {canSubmit && (
              <Button onClick={handleSubmitToFinance} disabled={actionLoading}>
                {actionLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Send className="h-4 w-4 mr-2" />
                )}
                Submit to Finance
              </Button>
            )}
            {canDownload && (
              <Button variant="outline" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Download Payslips
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Approval History */}
      {payroll.approvals && payroll.approvals.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Approval History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {payroll.approvals.map((approval) => (
                <div key={approval.id} className="flex items-start gap-4 border-l-2 border-gray-200 pl-4">
                  <div className="mt-1">
                    {approval.approved === 'true' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold capitalize">
                        {approval.approver_role.replace('_', ' ')}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {approval.decision_date
                          ? format(new Date(approval.decision_date), 'MMM dd, yyyy HH:mm')
                          : 'Pending'}
                      </div>
                    </div>
                    <div className="text-sm">
                      <Badge variant={approval.approved === 'true' ? 'default' : 'destructive'}>
                        {approval.approved === 'true' ? 'Approved' : 'Rejected'}
                      </Badge>
                    </div>
                    {approval.comments && (
                      <div className="mt-2 text-sm text-muted-foreground italic">
                        "{approval.comments}"
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Employee Details */}
      <Card>
        <CardHeader>
          <CardTitle>Employee Salary Details</CardTitle>
          <CardDescription>{payroll.entries.length} employees in this payroll</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Emp #</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Position</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead className="text-right">Basic</TableHead>
                  <TableHead className="text-right">Allowances</TableHead>
                  <TableHead className="text-right">Gross</TableHead>
                  <TableHead className="text-right">Deductions</TableHead>
                  <TableHead className="text-right">Net</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payroll.entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell className="font-medium">{entry.employee_number}</TableCell>
                    <TableCell>
                      {entry.first_name} {entry.last_name}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {entry.position || 'N/A'}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {entry.department || 'N/A'}
                    </TableCell>
                    <TableCell className="text-right">
                      ${parseFloat(entry.basic_salary.toString()).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      ${parseFloat(entry.allowances.toString()).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      ${parseFloat(entry.gross_salary.toString()).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right text-red-600">
                      ${parseFloat(entry.deductions.toString()).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-bold">
                      ${parseFloat(entry.net_salary.toString()).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
