import { api } from '@/lib/api-client';

export interface PayrollEntry {
  id?: string;
  payroll_id?: string;
  employee_id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  position: string | null;
  department: string | null;
  basic_salary: number;
  allowances: number;
  deductions: number;
  gross_salary?: number;
  net_salary?: number;
  currency: string;
  created_at?: string;
}

export interface PayrollApproval {
  id: string;
  payroll_id: string;
  approver_role: string;
  approver_id: string;
  approved: string;
  decision_date: string | null;
  comments: string | null;
  created_at: string;
}

export interface Payroll {
  id: string;
  month: number;
  year: number;
  payment_date: string;
  total_basic_salary: number;
  total_allowances: number;
  total_gross_salary: number;
  total_deductions: number;
  total_net_salary: number;
  status: 'DRAFT' | 'PENDING_FINANCE' | 'PENDING_CEO' | 'APPROVED' | 'REJECTED' | 'PROCESSED';
  created_by_id: string;
  processed_by_id: string | null;
  pdf_filename: string | null;
  created_at: string;
  updated_at: string;
  entries: PayrollEntry[];
  approvals: PayrollApproval[];
}

export interface EmployeePayrollSummary {
  employee_id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  position: string | null;
  department: string | null;
  basic_salary: number;
  has_active_contract: boolean;
  contract_monthly_salary: number | null;
}

export interface PayrollStats {
  total_payrolls: number;
  pending_finance_count: number;
  pending_ceo_count: number;
  approved_count: number;
  total_amount_this_month: number;
  total_amount_this_year: number;
}

export interface CreatePayrollRequest {
  month: number;
  year: number;
  payment_date: string;
  entries: PayrollEntry[];
}

export interface PayrollListResponse {
  payrolls: Payroll[];
  total: number;
  page: number;
  page_size: number;
}

export const payrollService = {
  // Get active employees for payroll
  async getEmployeesForPayroll(): Promise<EmployeePayrollSummary[]> {
    return api.get('/payroll/employees');
  },

  // Create payroll
  async createPayroll(data: CreatePayrollRequest): Promise<Payroll> {
    return api.post('/payroll', data);
  },

  // Get payroll list
  async listPayrolls(params: {
    page?: number;
    page_size?: number;
    status?: string;
    year?: number;
  }): Promise<PayrollListResponse> {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.set('page', params.page.toString());
    if (params.page_size) queryParams.set('page_size', params.page_size.toString());
    if (params.status) queryParams.set('status', params.status);
    if (params.year) queryParams.set('year', params.year.toString());
    
    return api.get(`/payroll?${queryParams.toString()}`);
  },

  // Get payroll by ID
  async getPayroll(payrollId: string): Promise<Payroll> {
    return api.get(`/payroll/${payrollId}`);
  },

  // Update payroll
  async updatePayroll(
    payrollId: string,
    data: Partial<CreatePayrollRequest>
  ): Promise<Payroll> {
    return api.put(`/payroll/${payrollId}`, data);
  },

  // Submit to Finance
  async submitToFinance(payrollId: string): Promise<Payroll> {
    return api.post(`/payroll/${payrollId}/submit`, {});
  },

  // Finance approve/reject
  async financeApprove(
    payrollId: string,
    approved: boolean,
    comments?: string
  ): Promise<Payroll> {
    return api.post(`/payroll/${payrollId}/finance-approve`, {
      approved,
      comments,
    });
  },

  // CEO approve/reject
  async ceoApprove(
    payrollId: string,
    approved: boolean,
    comments?: string
  ): Promise<Payroll> {
    return api.post(`/payroll/${payrollId}/ceo-approve`, {
      approved,
      comments,
    });
  },

  // Mark as processed
  async markProcessed(payrollId: string): Promise<Payroll> {
    return api.post(`/payroll/${payrollId}/mark-processed`, {});
  },

  // Delete payroll
  async deletePayroll(payrollId: string): Promise<void> {
    return api.delete(`/payroll/${payrollId}`);
  },

  // Get stats
  async getStats(): Promise<PayrollStats> {
    return api.get('/payroll/stats');
  },

  // Download payroll PDFs
  downloadPayroll(payrollId: string): string {
    return `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/payroll/${payrollId}/download`;
  },
};
