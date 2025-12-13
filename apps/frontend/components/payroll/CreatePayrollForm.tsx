'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';
import { CalendarIcon, Loader2, Trash2, Plus } from 'lucide-react';
import { payrollService, EmployeePayrollSummary, PayrollEntry } from '@/services/payroll.service';
import { useToast } from '@/hooks/use-toast';

interface CreatePayrollFormProps {
  onSuccess: () => void;
}

export default function CreatePayrollForm({ onSuccess }: CreatePayrollFormProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [employees, setEmployees] = useState<EmployeePayrollSummary[]>([]);
  const [selectedEmployees, setSelectedEmployees] = useState<Set<string>>(new Set());
  const [payrollData, setPayrollData] = useState<Map<string, PayrollEntry>>(new Map());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [paymentDate, setPaymentDate] = useState<Date | undefined>(new Date());
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const data = await payrollService.getEmployeesForPayroll();
      setEmployees(data);
      
      // Auto-select all employees and initialize with contract salary
      const initialSelected = new Set(data.map(emp => emp.employee_id));
      setSelectedEmployees(initialSelected);
      
      const initialData = new Map<string, PayrollEntry>();
      data.forEach(emp => {
        initialData.set(emp.employee_id, {
          employee_id: emp.employee_id,
          employee_number: emp.employee_number,
          first_name: emp.first_name,
          last_name: emp.last_name,
          position: emp.position,
          department: emp.department,
          basic_salary: parseFloat(emp.contract_monthly_salary?.toString() || '0') || 0,
          allowances: 0,
          deductions: 0,
          currency: 'USD',
        });
      });
      setPayrollData(initialData);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load employees',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleEmployee = (employeeId: string) => {
    const newSelected = new Set(selectedEmployees);
    if (newSelected.has(employeeId)) {
      newSelected.delete(employeeId);
    } else {
      newSelected.add(employeeId);
    }
    setSelectedEmployees(newSelected);
  };

  const updatePayrollEntry = (employeeId: string, field: keyof Omit<PayrollEntry, 'employee_id'>, value: number) => {
    const newData = new Map(payrollData);
    const entry = newData.get(employeeId);
    if (entry) {
      (entry as any)[field] = value;
      newData.set(employeeId, entry);
      setPayrollData(newData);
    }
  };

  const calculateTotals = () => {
    const selectedEntries = Array.from(selectedEmployees)
      .map(id => payrollData.get(id))
      .filter(Boolean) as PayrollEntry[];

    const totalBasic = selectedEntries.reduce((sum, e) => sum + e.basic_salary, 0);
    const totalAllowances = selectedEntries.reduce((sum, e) => sum + e.allowances, 0);
    const totalDeductions = selectedEntries.reduce((sum, e) => sum + e.deductions, 0);
    const totalGross = totalBasic + totalAllowances;
    const totalNet = totalGross - totalDeductions;

    return { totalBasic, totalAllowances, totalDeductions, totalGross, totalNet };
  };

  const handleSubmit = async () => {
    if (!paymentDate) {
      toast({
        title: 'Error',
        description: 'Please select a payment date',
        variant: 'destructive',
      });
      return;
    }

    if (selectedEmployees.size === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one employee',
        variant: 'destructive',
      });
      return;
    }

    try {
      setSubmitting(true);
      
      const entries = Array.from(selectedEmployees)
        .map(id => payrollData.get(id))
        .filter(Boolean) as PayrollEntry[];

      await payrollService.createPayroll({
        month,
        year,
        payment_date: format(paymentDate, 'yyyy-MM-dd'),
        entries,
      });

      toast({
        title: 'Success',
        description: 'Payroll created successfully',
      });

      onSuccess();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to create payroll',
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const totals = calculateTotals();

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Create New Payroll</CardTitle>
          <CardDescription>
            Select employees and enter salary details for the payroll period
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Payroll Period */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label>Month</Label>
              <Input
                type="number"
                min="1"
                max="12"
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
              />
            </div>
            <div>
              <Label>Year</Label>
              <Input
                type="number"
                min="2020"
                max="2100"
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
              />
            </div>
            <div>
              <Label>Payment Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left font-normal">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {paymentDate ? format(paymentDate, 'PPP') : <span>Pick a date</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={paymentDate}
                    onSelect={setPaymentDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <Alert>
            <AlertDescription>
              {selectedEmployees.size} employee(s) selected • Total Net: ${totals.totalNet.toLocaleString()}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Employee Salaries</CardTitle>
          <CardDescription>
            Review and adjust salary details. Basic salary is pre-filled from contracts.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={selectedEmployees.size === employees.length}
                      onCheckedChange={(checked: boolean) => {
                        if (checked) {
                          setSelectedEmployees(new Set(employees.map(e => e.employee_id)));
                        } else {
                          setSelectedEmployees(new Set());
                        }
                      }}
                    />
                  </TableHead>
                  <TableHead>Emp #</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Position</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead className="text-right">Basic Salary</TableHead>
                  <TableHead className="text-right">Allowances</TableHead>
                  <TableHead className="text-right">Deductions</TableHead>
                  <TableHead className="text-right">Net Salary</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employees.map((emp) => {
                  const entry = payrollData.get(emp.employee_id);
                  const isSelected = selectedEmployees.has(emp.employee_id);
                  const netSalary = entry 
                    ? entry.basic_salary + entry.allowances - entry.deductions 
                    : 0;

                  return (
                    <TableRow key={emp.employee_id} className={!isSelected ? 'opacity-50' : ''}>
                      <TableCell>
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => toggleEmployee(emp.employee_id)}
                        />
                      </TableCell>
                      <TableCell className="font-medium">{emp.employee_number}</TableCell>
                      <TableCell>
                        {emp.first_name} {emp.last_name}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {emp.position || 'N/A'}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {emp.department || 'N/A'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          value={entry?.basic_salary || 0}
                          onChange={(e) =>
                            updatePayrollEntry(emp.employee_id, 'basic_salary', parseFloat(e.target.value) || 0)
                          }
                          className="w-32 text-right"
                          disabled={!isSelected}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          value={entry?.allowances || 0}
                          onChange={(e) =>
                            updatePayrollEntry(emp.employee_id, 'allowances', parseFloat(e.target.value) || 0)
                          }
                          className="w-32 text-right"
                          disabled={!isSelected}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          value={entry?.deductions || 0}
                          onChange={(e) =>
                            updatePayrollEntry(emp.employee_id, 'deductions', parseFloat(e.target.value) || 0)
                          }
                          className="w-32 text-right"
                          disabled={!isSelected}
                        />
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        ${netSalary.toLocaleString()}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Totals Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Payroll Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Basic Salary:</span>
              <span className="font-semibold">${totals.totalBasic.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Allowances:</span>
              <span className="font-semibold">${totals.totalAllowances.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Gross Salary:</span>
              <span className="font-semibold">${totals.totalGross.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Deductions:</span>
              <span className="font-semibold text-red-600">-${totals.totalDeductions.toLocaleString()}</span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="text-lg font-bold">Total Net Payable:</span>
              <span className="text-lg font-bold text-green-600">${totals.totalNet.toLocaleString()}</span>
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-2">
            <Button variant="outline" onClick={() => window.location.reload()}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Payroll
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
