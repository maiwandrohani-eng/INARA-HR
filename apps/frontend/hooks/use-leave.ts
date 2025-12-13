/**
 * React Query Hooks for Leave Management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { leaveService } from '@/services/leave.service'

export function useLeaveBalance() {
  return useQuery({
    queryKey: ['leaveBalance'],
    queryFn: () => leaveService.getLeaveBalance(),
  })
}

export function useLeaveRequests() {
  return useQuery({
    queryKey: ['leaveRequests'],
    queryFn: () => leaveService.getLeaveRequests(),
  })
}

export function useCreateLeaveRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: leaveService.createLeaveRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaveRequests'] })
      queryClient.invalidateQueries({ queryKey: ['leaveBalance'] })
    },
  })
}

export function useApproveLeaveRequest() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      leaveService.approveLeaveRequest(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaveRequests'] })
    },
  })
}
