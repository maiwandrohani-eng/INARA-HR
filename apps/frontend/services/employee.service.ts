/**
 * Employee Service
 * API calls for employee management
 */

import apiClient from '@/lib/api-client'

export interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  work_email: string
  status: string
  employment_type: string
  hire_date?: string
  department_id?: string
  position_id?: string
}

export interface CreateEmployeeData {
  employee_number: string
  first_name: string
  last_name: string
  work_email: string
  date_of_birth: string
  employment_type: string
  hire_date: string
  country_code: string
}

class EmployeeService {
  async getEmployees(skip: number = 0, limit: number = 100): Promise<Employee[]> {
    const response = await apiClient.get<Employee[]>('/employees', {
      params: { skip, limit },
    })
    return response.data
  }

  async getEmployee(id: string): Promise<Employee> {
    const response = await apiClient.get<Employee>(`/employees/${id}`)
    return response.data
  }

  async createEmployee(data: CreateEmployeeData): Promise<Employee> {
    const response = await apiClient.post<Employee>('/employees', data)
    return response.data
  }

  async updateEmployee(id: string, data: Partial<Employee>): Promise<Employee> {
    const response = await apiClient.patch<Employee>(`/employees/${id}`, data)
    return response.data
  }
}

export const employeeService = new EmployeeService()
