/**
 * Employee Files Service
 * Manages employee personal files, contracts, extensions, and resignations
 */

import { api } from '@/lib/api-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Debug: Log the API URL being used
if (typeof window !== 'undefined') {
  console.log('🔗 Employee Files Service - API URL:', API_BASE_URL);
  console.log('🔗 Environment NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
}

export interface EmployeeDocument {
  id: string;
  employee_id: string;
  category: string;
  title: string;
  description?: string;
  file_path: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  uploaded_by: string;
  uploaded_at: string;
  is_confidential: boolean;
  expiry_date?: string;
  notes?: string;
}

export interface EmploymentContract {
  id: string;
  employee_id: string;
  contract_number: string;
  position_title: string;
  location: string;
  contract_type: string;
  start_date: string;
  end_date: string;
  signed_date?: string;
  monthly_salary: number;
  currency: string;
  status: string;
  june_review_date?: string;
  december_review_date?: string;
  june_review_outcome?: string;
  december_review_outcome?: string;
  termination_date?: string;
  termination_reason?: string;
  notice_period_days: number;
}

export interface ContractExtension {
  id: string;
  contract_id: string;
  employee_id: string;
  extension_number: number;
  new_start_date: string;
  new_end_date: string;
  new_monthly_salary?: number;
  salary_change_reason?: string;
  new_position_title?: string;
  new_location?: string;
  terms_changes?: string;
  employee_accepted_at?: string;
  employee_signature_ip?: string;
  status: string;
  expires_at?: string;
  created_at: string;
}

export interface Resignation {
  id: string;
  employee_id: string;
  resignation_number: string;
  resignation_date: string;
  intended_last_working_day: string;
  reason: string;
  notice_period_days: number;
  supervisor_id?: string;
  supervisor_accepted_at?: string;
  supervisor_comments?: string;
  hr_accepted_by?: string;
  hr_accepted_at?: string;
  hr_comments?: string;
  ceo_accepted_by?: string;
  ceo_accepted_at?: string;
  ceo_comments?: string;
  approved_last_working_day?: string;
  exit_interview_completed: boolean;
  exit_interview_date?: string;
  status: string;
}

export interface PersonalFileSummary {
  employee_id: string;
  employee_name: string;
  employee_number: string;
  total_documents: number;
  active_contracts: number;
  pending_extensions: number;
  total_resignations: number;
  current_contract?: EmploymentContract;
  current_contract_end_date?: string;
  days_until_contract_end?: number;
  recent_documents: EmployeeDocument[];
  pending_actions: string[];
}

class EmployeeFilesService {
  private getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  // ============= Documents =============
  
  async uploadDocument(formData: FormData): Promise<EmployeeDocument> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/employee-files/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type for FormData - browser will set it with boundary
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload document');
    }

    return response.json();
  }

  async getEmployeeDocuments(employeeId: string, category?: string): Promise<EmployeeDocument[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    
    const response = await fetch(
      `${API_BASE_URL}/employee-files/documents/employee/${employeeId}?${params}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(errorData.error?.message || `Failed to fetch documents (${response.status})`);
    }

    const data = await response.json();
    return data.documents || [];
  }

  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/employee-files/documents/${documentId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete document');
    }
  }

  // ============= Contracts =============

  async getEmployeeContracts(employeeId: string, includeInactive = false): Promise<EmploymentContract[]> {
    const params = new URLSearchParams();
    if (includeInactive) params.append('include_inactive', 'true');
    
    const response = await fetch(
      `${API_BASE_URL}/employee-files/contracts/employee/${employeeId}?${params}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch contracts');
    }

    const data = await response.json();
    return data.contracts || [];
  }

  async getActiveContract(employeeId: string): Promise<EmploymentContract | null> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/contracts/employee/${employeeId}/active`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error('Failed to fetch active contract');
    }

    return response.json();
  }

  async createContract(contractData: {
    employee_id: string;
    contract_number: string;
    position_title: string;
    location: string;
    contract_type: string;
    start_date: string;
    end_date: string;
    monthly_salary: number;
    currency: string;
    notice_period_days?: number;
    signed_date?: string;
  }): Promise<EmploymentContract> {
    const response = await fetch(`${API_BASE_URL}/employee-files/contracts`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify(contractData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(errorData.error?.message || 'Failed to create contract');
    }

    return response.json();
  }

  // ============= Extensions =============

  async createExtension(extensionData: {
    contract_id: string;
    employee_id: string;
    new_start_date: string;
    new_end_date: string;
    new_monthly_salary?: number;
    salary_change_reason?: string;
    new_position_title?: string;
    new_location?: string;
    terms_changes?: string;
  }): Promise<ContractExtension> {
    return api.post('/employee-files/extensions', extensionData);
  }

  async acceptExtension(extensionId: string): Promise<ContractExtension> {
    // Get client IP (in real app, backend should handle this)
    const employee_signature_ip = '0.0.0.0'; // Placeholder
    
    return api.post(`/employee-files/extensions/${extensionId}/accept`, {
      employee_signature_ip
    });
  }

  async getPendingExtensions(employeeId?: string): Promise<ContractExtension[]> {
    const params = new URLSearchParams();
    if (employeeId) params.append('employee_id', employeeId);
    
    const response = await fetch(
      `${API_BASE_URL}/employee-files/extensions/pending?${params}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch pending extensions');
    }

    const data = await response.json();
    return data.extensions || [];
  }

  // ============= Resignations =============

  async submitResignation(resignationData: {
    employee_id: string;
    resignation_date: string;
    intended_last_working_day: string;
    reason: string;
    supervisor_id?: string;
    notice_period_days?: number;
  }): Promise<Resignation> {
    const response = await fetch(`${API_BASE_URL}/employee-files/resignations`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify(resignationData),
    });

    if (!response.ok) {
      throw new Error('Failed to submit resignation');
    }

    return response.json();
  }

  async approveResignationSupervisor(
    resignationId: string,
    comments?: string
  ): Promise<Resignation> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/resignations/${resignationId}/approve/supervisor`,
      {
        method: 'POST',
        headers: this.getAuthHeader(),
        body: JSON.stringify({ comments }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to approve resignation');
    }

    return response.json();
  }

  async approveResignationHR(
    resignationId: string,
    comments?: string
  ): Promise<Resignation> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/resignations/${resignationId}/approve/hr`,
      {
        method: 'POST',
        headers: this.getAuthHeader(),
        body: JSON.stringify({ comments }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to approve resignation');
    }

    return response.json();
  }

  async approveResignationCEO(
    resignationId: string,
    approved_last_working_day: string,
    comments?: string
  ): Promise<Resignation> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/resignations/${resignationId}/approve/ceo`,
      {
        method: 'POST',
        headers: this.getAuthHeader(),
        body: JSON.stringify({ approved_last_working_day, comments }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to approve resignation');
    }

    return response.json();
  }

  async getEmployeeResignations(employeeId: string): Promise<Resignation[]> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/resignations/employee/${employeeId}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch resignations');
    }

    const data = await response.json();
    return data.resignations || [];
  }

  // ============= Personal File Summary =============

  async getPersonalFileSummary(employeeId: string): Promise<PersonalFileSummary> {
    const response = await fetch(
      `${API_BASE_URL}/employee-files/summary/${employeeId}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(errorData.error?.message || `Failed to fetch personal file summary (${response.status})`);
    }

    return response.json();
  }
}

export const employeeFilesService = new EmployeeFilesService();
