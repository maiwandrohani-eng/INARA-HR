/**
 * React Query Hooks for Approval Management
 * Provides caching, automatic refetching, and optimistic updates
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import apiClient from '@/lib/api-client'
import { handleApiError } from '@/lib/error-handler'

// Types
export interface ApprovalRequest {
  id: string
  request_type: string
  request_id: string
  employee_id: string
  employee_name: string
  approver_id: string
  status: string
  comments?: string
  submitted_at: string
  reviewed_at?: string
}

export interface ApprovalStats {
  total_pending: number
  leave_pending: number
  travel_pending: number
  timesheet_pending: number
  performance_pending: number
}

export interface ApprovalAction {
  comments?: string
}

// Query Keys
export const approvalKeys = {
  all: ['approvals'] as const,
  pending: () => [...approvalKeys.all, 'pending'] as const,
  stats: () => [...approvalKeys.all, 'stats'] as const,
  request: (id: string) => [...approvalKeys.all, 'request', id] as const,
}

/**
 * Get pending approvals for current user
 */
export function usePendingApprovals() {
  return useQuery({
    queryKey: approvalKeys.pending(),
    queryFn: async () => {
      const response = await apiClient.get('/approvals/pending')
      return response.data as ApprovalRequest[]
    },
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
    refetchOnWindowFocus: true,
  })
}

/**
 * Get approval statistics
 */
export function useApprovalStats() {
  return useQuery({
    queryKey: approvalKeys.stats(),
    queryFn: async () => {
      const response = await apiClient.get('/approvals/stats')
      return response.data as ApprovalStats
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 60 * 1000, // Refetch every minute
  })
}

/**
 * Approve request
 */
export function useApproveRequest() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async ({ requestId, data }: { requestId: string; data: ApprovalAction }) => {
      const response = await apiClient.post(`/approvals/requests/${requestId}/approve`, data)
      return response.data
    },
    onMutate: async ({ requestId }) => {
      // Cancel queries
      await queryClient.cancelQueries({ queryKey: approvalKeys.pending() })

      // Snapshot
      const previousApprovals = queryClient.getQueryData(approvalKeys.pending())

      // Optimistic update
      queryClient.setQueryData(approvalKeys.pending(), (old: any) =>
        old?.filter((req: ApprovalRequest) => req.id !== requestId)
      )

      // Update stats optimistically
      queryClient.setQueryData(approvalKeys.stats(), (old: any) => {
        if (!old) return old
        return {
          ...old,
          total_pending: Math.max(0, old.total_pending - 1),
        }
      })

      return { previousApprovals }
    },
    onError: (error, variables, context) => {
      // Rollback
      if (context?.previousApprovals) {
        queryClient.setQueryData(approvalKeys.pending(), context.previousApprovals)
      }

      const errorInfo = handleApiError(error)
      toast({
        title: errorInfo.title,
        description: errorInfo.message,
        variant: 'destructive',
      })
    },
    onSettled: () => {
      // Refetch
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() })
      queryClient.invalidateQueries({ queryKey: approvalKeys.stats() })
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Request approved successfully',
      })
    },
  })
}

/**
 * Reject request
 */
export function useRejectRequest() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async ({ requestId, data }: { requestId: string; data: ApprovalAction }) => {
      const response = await apiClient.post(`/approvals/requests/${requestId}/reject`, data)
      return response.data
    },
    onMutate: async ({ requestId }) => {
      await queryClient.cancelQueries({ queryKey: approvalKeys.pending() })

      const previousApprovals = queryClient.getQueryData(approvalKeys.pending())

      queryClient.setQueryData(approvalKeys.pending(), (old: any) =>
        old?.filter((req: ApprovalRequest) => req.id !== requestId)
      )

      queryClient.setQueryData(approvalKeys.stats(), (old: any) => {
        if (!old) return old
        return {
          ...old,
          total_pending: Math.max(0, old.total_pending - 1),
        }
      })

      return { previousApprovals }
    },
    onError: (error, variables, context) => {
      if (context?.previousApprovals) {
        queryClient.setQueryData(approvalKeys.pending(), context.previousApprovals)
      }

      const errorInfo = handleApiError(error)
      toast({
        title: errorInfo.title,
        description: errorInfo.message,
        variant: 'destructive',
      })
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: approvalKeys.pending() })
      queryClient.invalidateQueries({ queryKey: approvalKeys.stats() })
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Request rejected',
      })
    },
  })
}
