'use client'

export const dynamic = "force-dynamic";

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function TestAPIPage() {
  const [results, setResults] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const log = (msg: string) => {
    setResults(prev => [...prev, msg])
    console.log(msg)
  }

  const runTests = async () => {
    setResults([])
    setLoading(true)
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      log(`API URL: ${API_URL}`)
      
      // Test 1: Health check
      log('\n1️⃣ Testing health endpoint...')
      try {
        const healthUrl = API_URL.replace('/api/v1', '') + '/health';
        const resp = await fetch(healthUrl)
        log(`   Status: ${resp.status}`)
        const data = await resp.json()
        log(`   Response: ${JSON.stringify(data)}`)
      } catch (e: any) {
        log(`   ❌ Error: ${e.message}`)
      }
      
      // Test 2: Check localStorage
      log('\n2️⃣ Checking localStorage...')
      const token = localStorage.getItem('access_token')
      log(`   Token exists: ${!!token}`)
      if (token) {
        log(`   Token preview: ${token.substring(0, 30)}...`)
      }
      
      // Test 3: Login
      log('\n3️⃣ Testing login...')
      try {
        const resp = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'maiwand@inara.org',
            password: 'Maiwand@123'
          })
        })
        log(`   Status: ${resp.status}`)
        const data = await resp.json()
        const newToken = data.access_token
        log(`   New token obtained: ${!!newToken}`)
        if (newToken) {
          localStorage.setItem('access_token', newToken)
          log(`   ✅ Token saved to localStorage`)
        }
      } catch (e: any) {
        log(`   ❌ Error: ${e.message}`)
      }
      
      // Test 4: Get current user
      log('\n4️⃣ Testing /auth/me...')
      const currentToken = localStorage.getItem('access_token')
      if (currentToken) {
        try {
          const resp = await fetch(`${API_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
          })
          log(`   Status: ${resp.status}`)
          const data = await resp.json()
          log(`   User: ${data.email}`)
          log(`   Employee ID: ${data.employee_id}`)
        } catch (e: any) {
          log(`   ❌ Error: ${e.message}`)
        }
      } else {
        log(`   ⚠️ No token available`)
      }
      
      // Test 5: Personal file summary
      log('\n5️⃣ Testing personal file summary...')
      const empId = '8f65171e-aae6-4c76-84a9-e11fd67fe218'
      if (currentToken) {
        try {
          const resp = await fetch(`${API_URL}/employee-files/summary/${empId}`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
          })
          log(`   Status: ${resp.status}`)
          const data = await resp.json()
          log(`   Documents: ${data.total_documents}`)
          log(`   Contracts: ${data.active_contracts}`)
        } catch (e: any) {
          log(`   ❌ Error: ${e.message}`)
        }
      } else {
        log(`   ⚠️ No token available`)
      }
      
      log('\n✅ All tests complete!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Connection Test</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={runTests} disabled={loading}>
            {loading ? 'Running Tests...' : 'Run API Tests'}
          </Button>
          
          {results.length > 0 && (
            <pre className="bg-gray-100 p-4 rounded-lg overflow-auto max-h-96 text-sm">
              {results.join('\n')}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
