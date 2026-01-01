/**
 * Login Page
 */

'use client'

export const dynamic = "force-dynamic";

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/state/auth.store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { InaraLogo } from '@/components/ui/logo'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const login = useAuthStore((state) => state.login)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null) // Clear previous errors

    try {
      console.log('🚀 Starting login...')
      await login(email, password)
      console.log('✅ Login complete, redirecting...')
      setError(null) // Clear error on success
      toast({
        title: 'Login successful',
        description: 'Welcome back!',
      })
      router.push('/dashboard')
    } catch (error: any) {
      console.error('❌ Login error details:', error)
      console.error('❌ Error stack:', error?.stack)
      console.error('❌ Full error object:', JSON.stringify(error, null, 2))
      
      // Extract error message from various possible error structures
      let errorMessage = 'Invalid credentials. Please try again.'
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.response?.data?.error?.message) {
        errorMessage = error.response.data.error.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Set error state so it persists
      setError(errorMessage)
      
      toast({
        title: 'Login failed',
        description: errorMessage,
        variant: 'destructive',
        duration: 10000, // Show for 10 seconds instead of default
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-white to-cyan-50">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <InaraLogo className="w-20 h-20" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
            INARA HRIS
          </CardTitle>
          <CardDescription className="text-center">
            Enter your credentials to access the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md space-y-2">
                <div><strong>Error:</strong> {error}</div>
                {error.toLowerCase().includes('verify') && (
                  <div className="pt-2 border-t border-red-200 space-y-2">
                    <p className="text-xs text-red-700">Need to verify your email?</p>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={async () => {
                          if (!email) {
                            toast({
                              title: 'Email required',
                              description: 'Please enter your email first.',
                              variant: 'destructive',
                            })
                            return
                          }
                          try {
                            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/resend-verification`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ email })
                            })
                            const data = await response.json()
                            if (response.ok) {
                              toast({
                                title: 'Verification email sent',
                                description: 'Please check your email for the verification link.',
                              })
                            } else {
                              toast({
                                title: 'Failed to send verification',
                                description: data.detail || 'Please try again later.',
                                variant: 'destructive',
                              })
                            }
                          } catch (err) {
                            toast({
                              title: 'Error',
                              description: 'Failed to resend verification email.',
                              variant: 'destructive',
                            })
                          }
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        Resend verification email
                      </button>
                      <span className="text-xs text-gray-400">|</span>
                      <Link href="/verify-email" className="text-xs text-blue-600 hover:text-blue-800 underline">
                        Go to verification page
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
