/**
 * Dashboard Home Page - Dynamic Role-Based Dashboard
 */

'use client'

import { useEffect, useState } from 'react'
import { EmployeeDashboard } from '@/components/dashboard/EmployeeDashboard'
import { SupervisorDashboard } from '@/components/dashboard/SupervisorDashboard'
import { OrganizationChart } from '@/components/organization/OrganizationChart'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function DashboardPage() {
  const [userRole, setUserRole] = useState<'employee' | 'supervisor' | 'both'>('employee')
  const [loading, setLoading] = useState(true)
  const [hasApprovalRights, setHasApprovalRights] = useState(false)

  useEffect(() => {
    checkUserRole()
  }, [])

  const checkUserRole = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/employee', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        // Show supervisor section if user has approvals data
        setHasApprovalRights(data.approvals !== null && data.approvals !== undefined)
      }
    } catch (error) {
      console.error('Error checking user role:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Show employee dashboard with supervisor section if they have approval rights
  return (
    <div className="space-y-6">
      <EmployeeDashboard showSupervisorSection={hasApprovalRights} />
    </div>
  )
}
