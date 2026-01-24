import { useState, useEffect } from 'react'
import { API_BASE_URL } from '@/lib/api-config'

export interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  work_email: string
  phone?: string
  mobile?: string
  department_id?: string
  position_id?: string
  manager_id?: string
  work_location?: string
  status: string
  employment_type: string
  hire_date?: string
}

export function useEmployees() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEmployees = async () => {
    try {
      setLoading(true)
      setError(null)
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        console.warn('No authentication token found')
        setError('Not authenticated')
        setEmployees([])
        setLoading(false)
        return
      }
      
      const response = await fetch(`${API_BASE_URL}/employees/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Prevent caching
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Employees loaded:', data.length)
        setEmployees(data)
      } else {
        const errorText = await response.text()
        console.error('Failed to fetch employees:', response.status, errorText)
        setError(`Failed to fetch employees: ${response.status}`)
        setEmployees([])
      }
    } catch (err) {
      console.error('Failed to fetch employees:', err)
      setError('Failed to fetch employees')
      setEmployees([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmployees()
  }, [])

  return {
    employees,
    loading,
    error,
    refetch: fetchEmployees
  }
}

export function getEmployeeFullName(employee: Employee): string {
  return `${employee.first_name} ${employee.last_name}`
}

export function getEmployeeDisplayText(employee: Employee): string {
  return `${employee.employee_number} - ${getEmployeeFullName(employee)}`
}
