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
  Wallet
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'My Personal File', href: '/dashboard/my-personal-file', icon: UserCircle, employeeOnly: true },
  { name: 'Employees', href: '/dashboard/employees', icon: Users },
  { name: 'Organization Chart', href: '/dashboard/organization', icon: Network },
  { name: 'Recruitment', href: '/dashboard/recruitment', icon: Briefcase },
  { name: 'Leave & Attendance', href: '/dashboard/leave', icon: Calendar },
  { name: 'Timesheets', href: '/dashboard/timesheets', icon: Clock },
  { name: 'Performance', href: '/dashboard/performance', icon: TrendingUp },
  { name: 'Learning', href: '/dashboard/learning', icon: GraduationCap },
  { name: 'Payroll', href: '/dashboard/payroll', icon: Wallet, roles: ['admin', 'hr_manager', 'finance_manager', 'ceo'] },
  { name: 'Compensation', href: '/dashboard/compensation', icon: DollarSign },
  { name: 'Safeguarding', href: '/dashboard/safeguarding', icon: Shield },
  { name: 'Grievance', href: '/dashboard/grievance', icon: FileText },
  { name: 'Travel', href: '/dashboard/travel', icon: Plane },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Admin', href: '/dashboard/admin', icon: Settings },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
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

          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              
              // Filter based on role restrictions
              if (item.roles && !item.roles.some(role => user?.roles?.includes(role))) {
                return null
              }
              
              // Filter employee-only items
              if (item.employeeOnly && user?.roles?.includes('admin')) {
                return null
              }
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-pink-600 to-cyan-600 text-white shadow-sm'
                      : 'text-gray-300 hover:bg-gray-900 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
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
