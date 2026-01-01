'use client'

export const dynamic = "force-dynamic";

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { BookOpen, ArrowLeft, Loader2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function UserManualPage() {
  const router = useRouter()
  const [manualHtml, setManualHtml] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchManual()
  }, [])

  const fetchManual = async () => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('Not authenticated. Please log in.')
      }
      
      const response = await fetch(`${baseUrl}/admin/user-manual`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/html',
          'Content-Type': 'text/html'
        }
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('API Error:', response.status, errorText)
        if (response.status === 401 || response.status === 403) {
          throw new Error('Authentication failed. Please log in again.')
        } else if (response.status === 404) {
          throw new Error('User manual not found. Please contact support.')
        }
        throw new Error(`Failed to load user manual (${response.status})`)
      }

      const html = await response.text()
      setManualHtml(html)
    } catch (err: any) {
      console.error('Error fetching manual:', err)
      setError(err.message || 'Failed to load user manual. Please try again later.')
    } finally {
      setLoading(false)
    }
  }


  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-pink-600 mx-auto" />
          <p className="mt-4 text-gray-600">Loading user manual...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
            <Button onClick={() => router.back()} className="mt-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => router.back()}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <BookOpen className="w-8 h-8 text-pink-600" />
              User Manual
            </h1>
            <p className="text-gray-600 mt-1">INARA HR Management System</p>
          </div>
        </div>
      </div>

      {/* Manual Content */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div 
          className="p-8 prose prose-slate max-w-none"
          dangerouslySetInnerHTML={{ __html: manualHtml }}
        />
      </div>
    </div>
  )
}

