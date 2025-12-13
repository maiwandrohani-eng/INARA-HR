/**
 * Leave Service
 * API calls for leave management
 */

import apiClient from '@/lib/api-client'

export interface LeaveRequest {
  id: string
  employee_id: string
  leave_type: string
  start_date: string
  end_date: string
  total_days: number
  status: string
  reason?: string
}

export interface LeaveBalance {
  leave_type: string
  total_days: number
  used_days: number
  available_days: number
}

class LeaveService {
  async getLeaveBalance(): Promise<LeaveBalance[]> {
    const response = await apiClient.get<LeaveBalance[]>('/leave/balance')
    return response.data
  }

  async getLeaveRequests(): Promise<LeaveRequest[]> {
    const response = await apiClient.get<LeaveRequest[]>('/leave/requests')
    return response.data
  }

  async createLeaveRequest(data: {
    leave_type: string
    start_date: string
    end_date: string
    reason: string
  }): Promise<LeaveRequest> {
    const response = await apiClient.post<LeaveRequest>('/leave/requests', data)
    return response.data
  }

  async approveLeaveRequest(id: string, notes?: string): Promise<void> {
    await apiClient.post(`/leave/requests/${id}/approve`, {
      status: 'approved',
      notes,
    })
  }

  async rejectLeaveRequest(id: string, notes: string): Promise<void> {
    await apiClient.post(`/leave/requests/${id}/approve`, {
      status: 'rejected',
      notes,
    })
  }

  async exportLeaveRequestPDF(id: string): Promise<Blob> {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/leave/requests/${id}/export`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error('Failed to export PDF')
    }
    return await response.blob()
  }
}

export const leaveService = new LeaveService()
