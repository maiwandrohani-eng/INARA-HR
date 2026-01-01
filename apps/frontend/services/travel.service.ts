/**
 * Travel Service
 * API calls for travel management
 */

import apiClient from '@/lib/api-client'

export interface TravelRequest {
  id: string
  employee_id: string
  destination: string
  purpose: string
  start_date: string
  end_date: string
  status: string
  transport_mode?: string
  estimated_cost?: number
}

class TravelService {
  async getTravelRequests(): Promise<TravelRequest[]> {
    const response = await apiClient.get<TravelRequest[]>('/travel/requests')
    return response.data
  }

  async createTravelRequest(data: {
    destination: string
    purpose: string
    start_date: string
    end_date: string
    transport_mode?: string
    estimated_cost?: number
  }): Promise<TravelRequest> {
    const response = await apiClient.post<TravelRequest>('/travel/requests', data)
    return response.data
  }

  async exportTravelRequestPDF(id: string): Promise<Blob> {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/travel/requests/${id}/export`, {
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

export const travelService = new TravelService()
