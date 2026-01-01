'use client';

export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { payrollService, PayrollStats } from '@/services/payroll.service';
import { useAuthStore } from '@/state/auth.store';
import CreatePayrollForm from '@/components/payroll/CreatePayrollForm';
import PayrollList from '@/components/payroll/PayrollList';
import ApprovalQueue from '@/components/payroll/ApprovalQueue';

export default function PayrollPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<PayrollStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await payrollService.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load payroll stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Payroll Management</h1>
        <p className="text-muted-foreground">
          Process monthly payroll, manage approvals, and download payslips
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Payrolls</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_payrolls || 0}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Finance</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_finance_count || 0}</div>
            <p className="text-xs text-muted-foreground">Awaiting Finance review</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending CEO</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_ceo_count || 0}</div>
            <p className="text-xs text-muted-foreground">Awaiting CEO approval</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.approved_count || 0}</div>
            <p className="text-xs text-muted-foreground">Ready for payment</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="create">Create Payroll</TabsTrigger>
          <TabsTrigger value="approvals">Approvals</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>This Month</CardTitle>
                <CardDescription>Total payable for current month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  ${stats?.total_amount_this_month.toLocaleString() || '0'}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>This Year</CardTitle>
                <CardDescription>Total payable for {new Date().getFullYear()}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  ${stats?.total_amount_this_year.toLocaleString() || '0'}
                </div>
              </CardContent>
            </Card>
          </div>

          <PayrollList status="recent" onRefresh={loadStats} />
        </TabsContent>

        <TabsContent value="create">
          <CreatePayrollForm onSuccess={loadStats} />
        </TabsContent>

        <TabsContent value="approvals">
          <ApprovalQueue 
            userRole={user?.roles?.[0] || 'employee'} 
            onRefresh={loadStats} 
          />
        </TabsContent>

        <TabsContent value="history">
          <PayrollList status="all" onRefresh={loadStats} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
