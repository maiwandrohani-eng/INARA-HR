
/**
 * Email Verification Page
 */

'use client'
export const dynamic = "force-dynamic";

import React, { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { InaraLogo } from '@/components/ui/logo'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [token, setToken] = useState('')
  const [email, setEmail] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [isResending, setIsResending] = useState(false)
  const [isVerified, setIsVerified] = useState(false)

  useEffect(() => {
    // Check if token is in URL
    const tokenParam = searchParams.get('token')
    if (tokenParam) {
      setToken(tokenParam)
      handleVerify(tokenParam)
    }
  }, [searchParams])

  const handleVerify = async (verifyToken?: string) => {
    const tokenToUse = verifyToken || token
    if (!tokenToUse) {
      toast({
        title: 'Token required',
        description: 'Please enter your verification token.',
        variant: 'destructive',
      })
      return
    }

    setIsVerifying(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/verify-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenToUse })
      })

      const data = await response.json()

      if (response.ok) {
        setIsVerified(true)
        toast({
          title: 'Email verified!',
          description: 'Your email has been verified. You can now log in.',
        })
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } else {
        toast({
          title: 'Verification failed',
          description: data.detail || 'Invalid or expired token. Please request a new one.',
          variant: 'destructive',
        })
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to verify email. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsVerifying(false)
    }
  }

  const handleResend = async () => {
    if (!email) {
      toast({
        title: 'Email required',
        description: 'Please enter your email address.',
        variant: 'destructive',
      })
      return
    }

    setIsResending(true)
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
          title: 'Failed to send',
          description: data.detail || 'Please try again later.',
          variant: 'destructive',
        })
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'Failed to resend verification email.',
        variant: 'destructive',
      })
    } finally {
      setIsResending(false)
    }
  }

  if (isVerified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-white to-cyan-50">
        <Card className="w-full max-w-md shadow-xl">
          <CardHeader className="space-y-4 text-center">
            <div className="flex justify-center">
              <InaraLogo className="w-20 h-20" />
            </div>
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
              Email Verified!
            </CardTitle>
            <CardDescription className="text-center">
              Your email has been verified successfully. Redirecting to login...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 via-white to-cyan-50">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <InaraLogo className="w-20 h-20" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-cyan-600 bg-clip-text text-transparent">
            Verify Your Email
          </CardTitle>
          <CardDescription className="text-center">
            Enter your verification token or request a new one
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Verify with Token */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="token">Verification Token</Label>
              <Input
                id="token"
                type="text"
                placeholder="Enter token from email"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                disabled={isVerifying}
              />
            </div>
            <Button 
              type="button" 
              className="w-full" 
              onClick={() => handleVerify()}
              disabled={isVerifying || !token}
            >
              {isVerifying ? 'Verifying...' : 'Verify Email'}
            </Button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-muted-foreground">Or</span>
            </div>
          </div>

          {/* Resend Verification */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isResending}
              />
            </div>
            <Button 
              type="button" 
              variant="outline" 
              className="w-full" 
              onClick={handleResend}
              disabled={isResending || !email}
            >
              {isResending ? 'Sending...' : 'Resend Verification Email'}
            </Button>
          </div>

          <div className="text-center">
            <Button
              type="button"
              variant="link"
              onClick={() => router.push('/login')}
              className="text-sm"
            >
              Back to Login
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

