'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Settings, Users, Globe, DollarSign, Shield, Database, Building2, Calendar } from 'lucide-react'
import { UserManagementDialog } from '@/components/forms/UserManagementDialog'
import { PermissionsDialog } from '@/components/forms/PermissionsDialog'
import { CountryConfigDialog } from '@/components/forms/CountryConfigDialog'
import { SalaryBandsDialog } from '@/components/forms/SalaryBandsDialog'
import { DatabaseDialog } from '@/components/forms/DatabaseDialog'
import { SystemSettingsDialog } from '@/components/forms/SystemSettingsDialog'
import { DepartmentsPositionsDialog } from '@/components/forms/DepartmentsPositionsDialog'
import { LeavePoliciesDialog } from '@/components/forms/LeavePoliciesDialog'

export default function AdminPage() {
  const [showUserManagement, setShowUserManagement] = useState(false)
  const [showPermissions, setShowPermissions] = useState(false)
  const [showCountryConfig, setShowCountryConfig] = useState(false)
  const [showSalaryBands, setShowSalaryBands] = useState(false)
  const [showDatabase, setShowDatabase] = useState(false)
  const [showSystemSettings, setShowSystemSettings] = useState(false)
  const [showDepartmentsPositions, setShowDepartmentsPositions] = useState(false)
  const [showLeavePolicies, setShowLeavePolicies] = useState(false)

  const handleConfigure = (sectionTitle: string) => {
    switch (sectionTitle) {
      case 'User Management':
        setShowUserManagement(true)
        break
      case 'Permissions':
        setShowPermissions(true)
        break
      case 'Country Configurations':
        setShowCountryConfig(true)
        break
      case 'Salary Bands':
        setShowSalaryBands(true)
        break
      case 'Database':
        setShowDatabase(true)
        break
      case 'System Settings':
        setShowSystemSettings(true)
        break
      case 'Departments & Positions':
        setShowDepartmentsPositions(true)
        break
      case 'Leave Policies':
        setShowLeavePolicies(true)
        break
      case 'Country Configurations':
        alert('Country configuration module: Set country-specific settings, currencies, and regulations')
        break
      case 'Salary Bands':
        alert('Salary bands module: Define salary structures and compensation ranges by role')
        break
      case 'Permissions':
        alert('Permissions module: Configure role-based access control and user permissions')
        break
      case 'System Settings':
        alert('System settings module: Configure email settings, notifications, and general preferences')
        break
      case 'Database':
        alert('Database module: Backup, restore, and maintain database health')
        break
      default:
        alert(`${sectionTitle} configuration module`)
    }
  }

  const sections = [
    {
      title: 'User Management',
      description: 'Manage system users and roles',
      icon: Users,
      color: 'text-blue-600',
    },
    {
      title: 'Departments & Positions',
      description: 'Manage departments and job positions',
      icon: Building2,
      color: 'text-indigo-600',
    },
    {
      title: 'Country Configurations',
      description: 'Configure country-specific settings',
      icon: Globe,
      color: 'text-green-600',
    },
    {
      title: 'Leave Policies',
      description: 'Manage leave types and allowances',
      icon: Calendar,
      color: 'text-teal-600',
    },
    {
      title: 'Salary Bands',
      description: 'Set up salary structures',
      icon: DollarSign,
      color: 'text-purple-600',
    },
    {
      title: 'Permissions',
      description: 'Manage role permissions',
      icon: Shield,
      color: 'text-red-600',
    },
    {
      title: 'System Settings',
      description: 'Configure system preferences',
      icon: Settings,
      color: 'text-gray-600',
    },
    {
      title: 'Database',
      description: 'Database backup and maintenance',
      icon: Database,
      color: 'text-orange-600',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">System Administration</h1>
        <p className="text-gray-500 mt-2">Manage system settings and configurations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((section) => {
          const IconComponent = section.icon
          return (
            <Card key={section.title} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardContent className="pt-6">
                <IconComponent className={`w-12 h-12 ${section.color} mb-4`} />
                <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                <p className="text-sm text-gray-500 mb-4">{section.description}</p>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleConfigure(section.title)}
                >
                  Configure
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Version</p>
              <p className="font-semibold">1.0.0</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Environment</p>
              <p className="font-semibold">Development</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Database</p>
              <p className="font-semibold">PostgreSQL 14</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Backup</p>
              <p className="font-semibold">Never</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <UserManagementDialog open={showUserManagement} onOpenChange={setShowUserManagement} />
      <PermissionsDialog open={showPermissions} onOpenChange={setShowPermissions} />
      <CountryConfigDialog open={showCountryConfig} onOpenChange={setShowCountryConfig} />
      <SalaryBandsDialog open={showSalaryBands} onOpenChange={setShowSalaryBands} />
      <DatabaseDialog open={showDatabase} onOpenChange={setShowDatabase} />
      <SystemSettingsDialog open={showSystemSettings} onOpenChange={setShowSystemSettings} />
      <DepartmentsPositionsDialog open={showDepartmentsPositions} onOpenChange={setShowDepartmentsPositions} />
      <LeavePoliciesDialog open={showLeavePolicies} onOpenChange={setShowLeavePolicies} />
    </div>
  )
}
