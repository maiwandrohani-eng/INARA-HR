'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ArrowLeft, Edit, FileText } from 'lucide-react'
import { Employee } from '@/hooks/useEmployees'
import PersonalFileTab from '@/components/dashboard/PersonalFileTab'

interface CurrentUser {
  id: string
  employee_id?: string
  role: string
  permissions: string[]
}

export default function ViewEmployeePage() {
  const params = useParams()
  const router = useRouter()
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshKey, setRefreshKey] = useState(0)

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  // Extract permission names from the user's roles
  const userPermissions = currentUser?.roles?.flatMap((role: any) => 
    role.permissions?.map((p: any) => p.name) || []
  ) || [];
  
  const userRoles = currentUser?.roles?.map((role: any) => role.name) || [];

  const isOwner = currentUser?.employee_id === params.id;
  const isHR = userRoles.includes('hr') || userRoles.includes('admin') || 
               userPermissions.includes('hr:admin') || userPermissions.includes('hr:write') || 
               userPermissions.includes('admin:all');
  const isCEO = userRoles.includes('ceo') || userRoles.includes('admin') || 
                userPermissions.includes('ceo:all') || userPermissions.includes('admin:all');
  const [isSupervisor, setIsSupervisor] = useState(false);
  
  // Check if current user is supervisor of this employee
  useEffect(() => {
    const checkSupervisorStatus = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/dashboard/is-supervisor-of/${params.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setIsSupervisor(data.is_supervisor || false);
        }
      } catch (error) {
        console.error('Failed to check supervisor status:', error);
      }
    };
    
    if (params.id && currentUser?.employee_id) {
      checkSupervisorStatus();
    }
  }, [params.id, currentUser?.employee_id]);
  
  console.log('🔐 Permissions check:', { isOwner, isHR, isCEO, userRoles, userPermissions });

  useEffect(() => {
    fetchEmployee()
  }, [params.id, refreshKey])

  // Listen for route changes to force refresh
  useEffect(() => {
    setRefreshKey(prev => prev + 1)
  }, [router])

  const fetchEmployee = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      console.log('🔍 Fetching employee data...');
      console.log('API URL:', API_BASE_URL);
      console.log('Employee ID from URL:', params.id);
      console.log('Token:', token ? 'Present' : 'Missing');
      
      // Fetch employee data
      const response = await fetch(`${API_BASE_URL}/employees/${params.id}?t=${Date.now()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        cache: 'no-store',
      })

      console.log('Employee fetch response status:', response.status);

      if (response.ok) {
        const data = await response.json()
        setEmployee(data)
        console.log('✅ Employee loaded:', data);
      } else if (response.status === 404) {
        console.error('❌ Employee not found with ID:', params.id);
        alert(`Employee not found (ID: ${params.id}). Redirecting to employees list.`);
        router.push('/dashboard/employees');
        return;
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to load employee:', response.status, errorText);
        alert(`Failed to load employee: ${errorText || response.statusText}`);
        router.push('/dashboard/employees');
        return;
      }

      // Fetch current user data
      const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (userResponse.ok) {
        const userData = await userResponse.json()
        setCurrentUser(userData)
        console.log('✅ Current user loaded:', userData);
      } else {
        console.warn('⚠️ Failed to load current user:', userResponse.status);
      }
    } catch (error) {
      console.error('❌ Error fetching employee:', error)
      alert(`Network error: ${error instanceof Error ? error.message : 'Failed to load employee'}`)
      router.push('/dashboard/employees');
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="p-6">Loading...</div>
  }

  if (!employee) {
    return <div className="p-6">Employee not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{employee.first_name} {employee.last_name}</h1>
            <p className="text-gray-500 mt-2">{employee.employee_number}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isOwner && (
            <Button 
              variant="outline" 
              onClick={() => router.push('/dashboard/my-personal-file')}
              className="border-pink-200 text-pink-600 hover:bg-pink-50"
            >
              <FileText className="w-4 h-4 mr-2" />
              My Personnel File
            </Button>
          )}
          {(isHR || isCEO) && (
            <Button 
              variant="outline" 
              onClick={() => router.push(`/dashboard/employees/${employee.id}?tab=personal-file`)}
              className="border-pink-200 text-pink-600 hover:bg-pink-50"
            >
              <FileText className="w-4 h-4 mr-2" />
              View Personnel File
            </Button>
          )}
          <Button onClick={() => router.push(`/dashboard/employees/${employee.id}/edit`)}>
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      <Tabs defaultValue="profile" className="mt-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="personal-file">Personal File</TabsTrigger>
          <TabsTrigger value="leave">Leave</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Employee Number</label>
                  <p className="text-sm">{employee.employee_number}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Full Name</label>
                  <p className="text-sm">{employee.first_name} {employee.last_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Work Email</label>
                  <p className="text-sm">{employee.work_email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Phone</label>
                  <p className="text-sm">{employee.phone || '-'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Mobile</label>
                  <p className="text-sm">{employee.mobile || '-'}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Employment Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <p className="text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {employee.status?.toUpperCase()}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Employment Type</label>
                  <p className="text-sm">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {employee.employment_type?.replace('_', ' ').toUpperCase()}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Work Location</label>
                  <p className="text-sm">{employee.work_location || '-'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Hire Date</label>
                  <p className="text-sm">{employee.hire_date || '-'}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="personal-file" className="mt-6">
          <PersonalFileTab
            employeeId={params.id as string}
            employeeName={`${employee.first_name} ${employee.last_name}`}
            employeeNumber={employee.employee_number}
            isOwner={isOwner}
            isHR={isHR}
            isCEO={isCEO}
            isSupervisor={isSupervisor}
          />
        </TabsContent>

        <TabsContent value="leave" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Leave Records</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-500">Leave records will be displayed here.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Performance Reviews</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-500">Performance reviews will be displayed here.</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
