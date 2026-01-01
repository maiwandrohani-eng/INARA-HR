export const dynamic = "force-dynamic";

/**
 * Organization Chart Page
 * Displays the organizational hierarchy
 */

'use client'

import { OrganizationChart } from '@/components/organization/OrganizationChart'

export default function OrganizationPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Organization Chart</h1>
        <p className="mt-2 text-gray-600">View and manage the organizational hierarchy</p>
      </div>
      
      <OrganizationChart />
    </div>
  )
}
