/**
 * Dashboard Layout
 * Main application layout with sidebar navigation
 */

'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/state/auth.store'
import { Button } from '@/components/ui/button'
import { InaraLogo } from '@/components/ui/logo'
import Link from 'next/link'
import { 
  Users, 
  Briefcase, 
  Calendar, 
  Clock, 
  TrendingUp, 
  GraduationCap,
  DollarSign,
  Shield,
  FileText,
  Plane,
  BarChart3,
  Settings,
  Home,
  LogOut,
  Network,
  UserCircle,
  Wallet,
  Heart,
  Laptop,
  Receipt,
  Bell,
  Scale,
  UserCheck,
  Smile,
  Target,
  DoorOpen,
  ChevronDown,
  ChevronRight
} from 'lucide-react'
import { useState } from 'react'

// Navigation structure with logical grouping
const navigationGroups = [
  // ===== EMPLOYEE SELF-SERVICE SECTION =====
  {
    title: 'My Workspace',
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: Home },
      { name: 'My Personnel File', href: '/dashboard/my-personal-file', icon: UserCircle, employeeOnly: true, priority: 'high' },
      { name: 'Pending Approvals', href: '/dashboard/approvals', icon: FileText, supervisorOnly: true },
      { name: 'Organization Chart', href: '/dashboard/organization', icon: Network },
    ]
  },
  
  // ===== MY REQUESTS SECTION =====
  {
    title: 'My Requests',
    items: [
      { name: 'Leave & Attendance', href: '/dashboard/leave', icon: Calendar },
      { name: 'Timesheets', href: '/dashboard/timesheets', icon: Clock },
      { name: 'Travel', href: '/dashboard/travel', icon: Plane },
      { name: 'File Grievance', href: '/dashboard/grievance', icon: FileText, employeeAction: true },
      { name: 'Report Safeguarding', href: '/dashboard/safeguarding', icon: Shield, employeeAction: true },
      { name: 'Performance Self Assessment', href: '/dashboard/performance', icon: TrendingUp, employeeAction: true },
    ]
  },
  
  // ===== HR MANAGEMENT SECTION =====
  {
    title: 'HR Management',
    hrOnly: true,
    items: [
      // Core HR Operations (Most frequently used)
      { name: 'Employees', href: '/dashboard/employees', icon: Users, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'], priority: 'high' },
      { name: 'Recruitment', href: '/dashboard/recruitment', icon: Briefcase, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'], priority: 'high' },
      
      // Performance & Development (HR Management View)
      { name: 'Performance Reviews', href: '/dashboard/performance', icon: TrendingUp, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'], priority: 'high', hrManagementView: true },
      { name: 'Learning', href: '/dashboard/learning', icon: GraduationCap, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Compensation & Benefits
      { name: 'Payroll', href: '/dashboard/payroll', icon: Wallet, roles: ['admin', 'hr_manager', 'finance_manager', 'ceo'], priority: 'high' },
      { name: 'Compensation', href: '/dashboard/compensation', icon: DollarSign, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Benefits', href: '/dashboard/benefits', icon: Heart, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Employee Relations (HR Management View)
      { name: 'Grievances', href: '/dashboard/grievance', icon: FileText, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'], hrManagementView: true },
      { name: 'Safeguarding Cases', href: '/dashboard/safeguarding', icon: Shield, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'], hrManagementView: true },
      { name: 'Engagement', href: '/dashboard/engagement', icon: Smile, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Operations
      { name: 'Assets', href: '/dashboard/assets', icon: Laptop, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Expenses', href: '/dashboard/expenses', icon: Receipt, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Strategic Planning
      { name: 'Workforce Planning', href: '/dashboard/workforce', icon: Target, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Succession Planning', href: '/dashboard/succession', icon: UserCheck, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Exit Management', href: '/dashboard/exit', icon: DoorOpen, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Analytics & Compliance
      { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Compliance', href: '/dashboard/compliance', icon: Scale, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      { name: 'Notifications', href: '/dashboard/notifications', icon: Bell, roles: ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'] },
      
      // Administration
      { name: 'Admin Settings', href: '/dashboard/admin', icon: Settings, roles: ['admin', 'ceo'] },
    ]
  },
]

// Helper function to check if user has HR/Admin roles
const hasHRAdminAccess = (userRoles: string[] = []) => {
  return userRoles.some(role => 
    ['admin', 'hr', 'hr_manager', 'hr_admin', 'ceo'].includes(role.toLowerCase())
  )
}

// Helper function to check if user has Admin/CEO roles
const hasAdminAccess = (userRoles: string[] = []) => {
  return userRoles.some(role => 
    ['admin', 'ceo'].includes(role.toLowerCase())
  )
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['My Workspace', 'My Requests']))

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  const userRoles = user?.roles || []
  const isHRAdmin = hasHRAdminAccess(userRoles)
  const isAdmin = hasAdminAccess(userRoles)

  const toggleGroup = (groupTitle: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(groupTitle)) {
      newExpanded.delete(groupTitle)
    } else {
      newExpanded.add(groupTitle)
    }
    setExpandedGroups(newExpanded)
  }

  // Filter and sort navigation items
  const getFilteredItems = (items: any[], groupTitle?: string) => {
    return items
      .filter((item) => {
        // For employee actions in "My Requests" - show to all employees (except if they're viewing HR management view)
        if (item.employeeAction) {
          // If user is HR and viewing "My Requests", still show employee actions (they can use them too)
          // But if viewing HR Management section, hide employee action items there
          if (groupTitle === 'HR Management' && item.hrManagementView) {
            return false // Hide employee actions from HR Management section
          }
          return true // Show employee actions in "My Requests" for everyone
        }

        // For HR management view items - only show in HR Management section, not in employee sections
        if (item.hrManagementView) {
          // Only show in HR Management section
          if (groupTitle !== 'HR Management') {
            return false
          }
          // Only show to HR users
          if (item.roles && !item.roles.some((role: string) => user?.roles?.includes(role))) {
            return false
          }
          return true
        }

        // Filter based on role restrictions
        if (item.roles && !item.roles.some((role: string) => user?.roles?.includes(role))) {
          return false
        }
        // Filter employee-only items
        if (item.employeeOnly && user?.roles?.includes('admin')) {
          return false
        }
        // Filter supervisor-only items (check if user has direct reports)
        if (item.supervisorOnly) {
          // For now, show to all users - can be enhanced with actual supervisor check
          return true
        }
        return true
      })
      .sort((a, b) => {
        // Prioritize high-priority items
        if (a.priority === 'high' && b.priority !== 'high') return -1
        if (b.priority === 'high' && a.priority !== 'high') return 1
        return 0
      })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-black border-r border-gray-800 shadow-sm">
        <div className="flex flex-col h-full">
          <div className="px-6 py-4 border-b border-gray-800">
            <div className="flex items-center gap-3 mb-3">
              <InaraLogo className="w-16 h-16 object-contain" />
              <h1 className="text-xl font-bold text-white">
                INARA HRIS
              </h1>
            </div>
            <p className="text-sm text-gray-400">{user?.email}</p>
          </div>

          <nav className="flex-1 px-4 py-4 space-y-4 overflow-y-auto">
            {navigationGroups.map((group) => {
              // Filter HR-only groups
              if (group.hrOnly && !isHRAdmin) {
                return null
              }

              const filteredItems = getFilteredItems(group.items, group.title)
              if (filteredItems.length === 0) {
                return null
              }

              const isExpanded = expandedGroups.has(group.title)
              const isHRGroup = group.title === 'HR Management'

              return (
                <div key={group.title} className="space-y-1">
                  {/* Group Header */}
                  {isHRGroup ? (
                    <button
                      onClick={() => toggleGroup(group.title)}
                      className="flex items-center justify-between w-full px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider hover:text-gray-300 transition-colors"
                    >
                      <span>{group.title}</span>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>
                  ) : (
                    <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                      {group.title}
                    </div>
                  )}

                  {/* Group Items */}
                  {(!isHRGroup || isExpanded) && (
                    <div className="space-y-1">
                      {filteredItems.map((item) => {
                        const isActive = pathname === item.href
                        
                        return (
                          <Link
                            key={item.name}
                            href={item.href}
                            className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all ${
                              isActive
                                ? 'bg-gradient-to-r from-pink-600 to-cyan-600 text-white shadow-sm'
                                : item.priority === 'high' && isHRGroup
                                ? 'text-gray-200 hover:bg-gray-800 hover:text-white'
                                : 'text-gray-300 hover:bg-gray-900 hover:text-white'
                            }`}
                          >
                            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
                            <span className="truncate">{item.name}</span>
                            {item.priority === 'high' && !isActive && (
                              <span className="ml-auto w-1.5 h-1.5 bg-pink-500 rounded-full flex-shrink-0"></span>
                            )}
                          </Link>
                        )
                      })}
                    </div>
                  )}

                  {/* Separator between sections */}
                  {group.title !== 'HR Management' && (
                    <div className="border-t border-gray-800 mt-3"></div>
                  )}
                </div>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-800">
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-300 hover:text-white hover:bg-gray-900"
              onClick={handleLogout}
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
