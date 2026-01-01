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
import { Loader2, Download, Eye, Trash2, Send } from 'lucide-react';
import { payrollService, Payroll } from '@/services/payroll.service';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';

interface PayrollListProps {
  status: 'recent' | 'all';
  onRefresh: () => void;
}

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

export default function PayrollList({ status, onRefresh }: PayrollListProps) {
  const { toast } = useToast();
  const router = useRouter();
  const [payrolls, setPayrolls] = useState<Payroll[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadPayrolls();
  }, [status]);

  const loadPayrolls = async () => {
    try {
      setLoading(true);
      const data = await payrollService.listPayrolls({
        page: 1,
        page_size: status === 'recent' ? 10 : 50,
      });
      setPayrolls(data.payrolls);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load payrolls',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitToFinance = async (payrollId: string) => {
    try {
      setActionLoading(payrollId);
      await payrollService.submitToFinance(payrollId);
      toast({
        title: 'Success',
        description: 'Payroll submitted to Finance for review',
      });
      loadPayrolls();
      onRefresh();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to submit payroll',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (payrollId: string) => {
    if (!confirm('Are you sure you want to delete this payroll?')) return;

    try {
      setActionLoading(payrollId);
      await payrollService.deletePayroll(payrollId);
      toast({
        title: 'Success',
        description: 'Payroll deleted successfully',
      });
      loadPayrolls();
      onRefresh();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to delete payroll',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownload = async (payrollId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${baseUrl}/payroll/${payrollId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `payroll_payslips_${Date.now()}.zip`;
      
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

  if (payrolls.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Payroll History</CardTitle>
          <CardDescription>No payrolls found</CardDescription>
        </CardHeader>
        <CardContent className="text-center py-12 text-muted-foreground">
          <p>No payroll records to display</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payroll {status === 'recent' ? 'Overview' : 'History'}</CardTitle>
        <CardDescription>
          {status === 'recent' ? 'Recent payroll batches' : 'All payroll records'}
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
                <TableHead>Status</TableHead>
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
                    <Badge className={statusColors[payroll.status]}>
                      {statusLabels[payroll.status]}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/dashboard/payroll/${payroll.id}`)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>

                    {payroll.status === 'DRAFT' && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSubmitToFinance(payroll.id)}
                          disabled={actionLoading === payroll.id}
                        >
                          {actionLoading === payroll.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Send className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(payroll.id)}
                          disabled={actionLoading === payroll.id}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </>
                    )}

                    {(payroll.status === 'APPROVED' || payroll.status === 'PROCESSED') && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(payroll.id)}
                        title="Download Payslips (PDF)"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
