
/**
 * My Personal File Page
 * Redirects employee to their own personal file
 */

'use client'
export const dynamic = "force-dynamic";

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'

export default function MyPersonalFilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (isMounted) {
      redirectToPersonalFile()
    }
  }, [isMounted])

  const redirectToPersonalFile = async () => {
    try {
      // Check if we're in the browser
      if (typeof window === 'undefined') {
        console.log('⚠️ Not in browser, skipping');
        return;
      }

      const token = localStorage.getItem('access_token')
      console.log('🔑 Token check:', token ? 'Present' : 'Missing');
      
      if (!token) {
        console.log('⚠️ No token, redirecting to login');
        router.push('/login')
        return
      }

      // Get current user info
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      console.log('📡 Fetching user data from', API_URL + '/auth/me');
      
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Failed to get user info:', errorText);
        throw new Error(`Failed to get user information (${response.status})`)
      }

      const userData = await response.json()
      console.log('✅ User data:', userData);
      
      // Check if user has employee_id
      if (!userData.employee_id) {
        console.error('❌ No employee_id in user data');
        setError('Your user account is not linked to an employee profile. Please contact HR.')
        setLoading(false)
        return
      }

      console.log('✅ Redirecting to employee:', userData.employee_id);
      // Redirect to employee's personal file
      router.push(`/dashboard/employees/${userData.employee_id}?tab=personal-file`)
    } catch (err) {
      console.error('❌ Error redirecting to personal file:', err)
      setError(`Failed to load your personal file: ${err instanceof Error ? err.message : 'Unknown error'}. Please try again or contact support.`)
      setLoading(false)
    }
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-red-500 text-5xl mb-4">⚠️</div>
              <h2 className="text-xl font-bold mb-2">Unable to Load Personal File</h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <div className="flex gap-2 justify-center">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-4 py-2 bg-gradient-to-r from-pink-600 to-cyan-600 text-white rounded-md hover:shadow-lg transition-shadow"
                >
                  Return to Dashboard
                </button>
                <button
                  onClick={() => {
                    setError(null);
                    setLoading(true);
                    redirectToPersonalFile();
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Try Again
                </button>
                <button
                  onClick={() => router.push('/login')}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Re-login
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading your personal file...</p>
      </div>
    </div>
  )
}
