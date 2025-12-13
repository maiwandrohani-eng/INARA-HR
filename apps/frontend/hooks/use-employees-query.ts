/**
 * React Query Hooks for Employee Management
 * Provides caching, automatic refetching, and optimistic updates
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import apiClient from '@/lib/api-client'
import { handleApiError } from '@/lib/error-handler'

// Types
export interface Employee {
  id: string
  employee_number: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  position?: string
  department?: string
  supervisor_id?: string
  status: string
  hire_date?: string
  country_code?: string
  created_at: string
}

export interface EmployeeCreate {
  first_name: string
  last_name: string
  email: string
  phone?: string
  position_id?: string
  department_id?: string
  supervisor_id?: string
  hire_date: string
  country_code: string
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {
  status?: string
}

// Query Keys
export const employeeKeys = {
  all: ['employees'] as const,
  lists: () => [...employeeKeys.all, 'list'] as const,
  list: (filters?: any) => [...employeeKeys.lists(), { filters }] as const,
  details: () => [...employeeKeys.all, 'detail'] as const,
  detail: (id: string) => [...employeeKeys.details(), id] as const,
}

/**
 * Get all employees with optional filters
 */
export function useEmployees(filters?: any) {
  return useQuery({
    queryKey: employeeKeys.list(filters),
    queryFn: async () => {
      const response = await apiClient.get('/employees', { params: filters })
      return response.data as Employee[]
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Get single employee by ID
 */
export function useEmployee(id: string, options?: Omit<UseQueryOptions<Employee>, 'queryKey' | 'queryFn'>) {
  return useQuery({
    queryKey: employeeKeys.detail(id),
    queryFn: async () => {
      const response = await apiClient.get(`/employees/${id}`)
      return response.data as Employee
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!id,
    ...options,
  })
}

/**
 * Create new employee
 */
export function useCreateEmployee() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async (data: EmployeeCreate) => {
      const response = await apiClient.post('/employees', data)
      return response.data
    },
    onSuccess: (newEmployee) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() })

      toast({
        title: 'Success',
        description: `Employee ${newEmployee.first_name} ${newEmployee.last_name} created successfully`,
      })
    },
    onError: (error) => {
      const errorInfo = handleApiError(error)
      toast({
        title: errorInfo.title,
        description: errorInfo.message,
        variant: 'destructive',
      })
    },
  })
}

/**
 * Update employee
 */
export function useUpdateEmployee() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: EmployeeUpdate }) => {
      const response = await apiClient.put(`/employees/${id}`, data)
      return response.data
    },
    onMutate: async ({ id, data }) => {
      // Cancel queries
      await queryClient.cancelQueries({ queryKey: employeeKeys.detail(id) })

      // Snapshot
      const previousEmployee = queryClient.getQueryData(employeeKeys.detail(id))

      // Optimistic update
      queryClient.setQueryData(employeeKeys.detail(id), (old: any) => ({
        ...old,
        ...data,
      }))

      return { previousEmployee }
    },
    onError: (error, { id }, context) => {
      // Rollback
      if (context?.previousEmployee) {
        queryClient.setQueryData(employeeKeys.detail(id), context.previousEmployee)
      }

      const errorInfo = handleApiError(error)
      toast({
        title: errorInfo.title,
        description: errorInfo.message,
        variant: 'destructive',
      })
    },
    onSettled: (data, error, { id }) => {
      // Refetch
      queryClient.invalidateQueries({ queryKey: employeeKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() })
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Employee updated successfully',
      })
    },
  })
}

/**
 * Delete employee (soft delete)
 */
export function useDeleteEmployee() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.delete(`/employees/${id}`)
      return response.data
    },
    onSuccess: () => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() })

      toast({
        title: 'Success',
        description: 'Employee deleted successfully',
      })
    },
    onError: (error) => {
      const errorInfo = handleApiError(error)
      toast({
        title: errorInfo.title,
        description: errorInfo.message,
        variant: 'destructive',
      })
    },
  })
}
