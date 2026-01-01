/**
 * Timesheet Service
 * API calls for timesheet management
 */

import apiClient from '@/lib/api-client'

export interface TimesheetEntry {
  id: string
  date: string
  hours: number
  description: string
}

export interface Timesheet {
  id: string
  employee_id: string
  start_date: string
  end_date: string
  total_hours: number
  status: string
  entries: TimesheetEntry[]
}

class TimesheetService {
  async getTimesheets(): Promise<Timesheet[]> {
    const response = await apiClient.get<{timesheets: Timesheet[]}>('/timesheets/')
    return response.data.timesheets
  }

  async createTimesheet(data: {
    start_date: string
    end_date: string
    entries: Omit<TimesheetEntry, 'id'>[]
  }): Promise<Timesheet> {
    const response = await apiClient.post<Timesheet>('/timesheets/', data)
    return response.data
  }

  async exportTimesheetPDF(id: string): Promise<Blob> {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/timesheets/${id}/export`, {
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

export const timesheetService = new TimesheetService()
