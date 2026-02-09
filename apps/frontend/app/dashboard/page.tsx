
/**
 * Dashboard Home Page - Dynamic Role-Based Dashboard
 * Optimized: Removed duplicate API call - EmployeeDashboard will determine supervisor section
 */

'use client'
export const dynamic = "force-dynamic";

import { EmployeeDashboard } from '@/components/dashboard/EmployeeDashboard'

export default function DashboardPage() {
  // EmployeeDashboard will fetch data once and determine if supervisor section should be shown
  // based on the approvals data it receives, eliminating the duplicate API call
  return (
    <div className="space-y-6">
      <EmployeeDashboard />
    </div>
  )
}
