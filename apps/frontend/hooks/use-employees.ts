/**
 * React Query Hooks for Employees
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeService, Employee, CreateEmployeeData } from '@/services/employee.service'

export function useEmployees(skip?: number, limit?: number) {
  return useQuery({
    queryKey: ['employees', skip, limit],
    queryFn: () => employeeService.getEmployees(skip, limit),
  })
}

export function useEmployee(id: string) {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeeService.getEmployee(id),
    enabled: !!id,
  })
}

export function useCreateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateEmployeeData) => employeeService.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}

export function useUpdateEmployee() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Employee> }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      queryClient.invalidateQueries({ queryKey: ['employee', variables.id] })
    },
  })
}
