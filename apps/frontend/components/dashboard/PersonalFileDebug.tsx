/**
 * Debug Component for Personal File Tab
 * This shows what data is being loaded
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function PersonalFileDebug({ employeeId }: { employeeId: string }) {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    const token = localStorage.getItem('access_token');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

    const info: any = {
      employeeId,
      token: token ? `${token.substring(0, 40)}...` : 'NO TOKEN',
      tokenLength: token ? token.length : 0,
      apiUrl,
      envVariable: process.env.NEXT_PUBLIC_API_URL,
      timestamp: new Date().toISOString(),
      tests: {},
      browserInfo: {
        userAgent: navigator.userAgent,
        online: navigator.onLine,
        protocol: window.location.protocol,
        hostname: window.location.hostname
      }
    };

    // Test auth/me endpoint to verify token
    try {
      console.log('Testing auth/me endpoint');
      const response = await fetch(`${apiUrl}/auth/me`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      const data = response.ok ? await response.json() : await response.text();
      info.tests.authMe = {
        status: response.status,
        ok: response.ok,
        data
      };
      console.log('Auth/me result:', data);
    } catch (error) {
      console.error('Auth/me error:', error);
      info.tests.authMe = { 
        error: String(error),
        message: error instanceof Error ? error.message : 'Unknown'
      };
    }

    // Test basic health endpoint (no auth)
    try {
      const healthUrl = `${API_BASE_URL.replace('/api/v1', '')}/health`;
      console.log('Testing health endpoint:', healthUrl);
      const response = await fetch(healthUrl, {
        method: 'GET',
        mode: 'cors',
      });
      const data = await response.json();
      info.tests.health = {
        status: response.status,
        ok: response.ok,
        data
      };
      console.log('Health check result:', data);
    } catch (error) {
      console.error('Health check error:', error);
      info.tests.health = { 
        error: String(error),
        message: error instanceof Error ? error.message : 'Unknown'
      };
    }

    // Test summary endpoint
    try {
      console.log('Testing summary endpoint:', `${apiUrl}/employee-files/summary/${employeeId}`);
      const response = await fetch(`${apiUrl}/employee-files/summary/${employeeId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      const responseText = await response.text();
      info.tests.summary = {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries()),
        data: responseText ? JSON.parse(responseText) : null
      };
    } catch (error) {
      console.error('Summary fetch error:', error);
      info.tests.summary = { 
        error: String(error),
        errorType: error?.constructor?.name,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      };
    }

    // Test documents endpoint
    try {
      const response = await fetch(`${apiUrl}/employee-files/documents/employee/${employeeId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      info.tests.documents = {
        status: response.status,
        ok: response.ok,
        data: response.ok ? await response.json() : await response.text()
      };
    } catch (error) {
      info.tests.documents = { error: String(error) };
    }

    // Test contracts endpoint
    try {
      const response = await fetch(`${apiUrl}/employee-files/contracts/employee/${employeeId}?include_inactive=true`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      info.tests.contracts = {
        status: response.status,
        ok: response.ok,
        data: response.ok ? await response.json() : await response.text()
      };
    } catch (error) {
      info.tests.contracts = { error: String(error) };
    }

    setDebugInfo(info);
    setLoading(false);
  };

  useEffect(() => {
    testAPI();
  }, [employeeId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Personal File Debug Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Button onClick={testAPI} disabled={loading}>
              {loading ? 'Testing...' : 'Refresh Tests'}
            </Button>
          </div>
          
          <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto max-h-96">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>
      </CardContent>
    </Card>
  );
}
