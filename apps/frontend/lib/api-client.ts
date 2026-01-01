'use client'

/**
 * API Client Configuration
 * Enhanced axios instance with retry logic, token refresh, and better error handling
 */

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

console.log('🌐 API Client initialized with baseURL:', API_URL)

// Test backend connectivity on initialization
const testBackendConnection = async () => {
  try {
    const response = await fetch(`${API_URL.replace('/api/v1', '')}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5 second timeout for health check
    })
    if (response.ok) {
      console.log('✅ Backend is reachable')
    } else {
      console.warn('⚠️ Backend responded but health check failed')
    }
  } catch (error) {
    console.error('❌ Cannot reach backend at', API_URL)
    console.error('   Make sure the backend server is running on port 8000')
    console.error('   Error:', error instanceof Error ? error.message : error)
  }
}

// Run connection test (non-blocking)
if (typeof window !== 'undefined') {
  testBackendConnection()
}

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Create axios instance with retry configuration
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds - increased for login/auth operations
})

// Retry configuration
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second

const shouldRetry = (error: AxiosError): boolean => {
  // Retry on network errors or 5xx server errors
  return !error.response || (error.response.status >= 500 && error.response.status < 600)
}

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', config.method?.toUpperCase(), config.baseURL + config.url)
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('❌ Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean; _retryCount?: number }

    // Handle network errors (connection refused, timeout, etc.)
    // Only treat as network error if there's no response AND it's a real network error
    if (!error.response && error.code !== 'ECONNABORTED') {
      // Check if it's a real network error by looking at error code
      const networkErrorCodes = ['ECONNREFUSED', 'ENOTFOUND', 'ETIMEDOUT', 'ECONNRESET']
      const isNetworkError = error.code && networkErrorCodes.includes(error.code)
      
      // Also check if error message indicates network issue
      const isNetworkMessage = error.message && (
        error.message.includes('Network Error') ||
        error.message.includes('ERR_NETWORK') ||
        error.message.includes('Failed to fetch') ||
        error.message.includes('fetch failed')
      )
      
      if (isNetworkError || isNetworkMessage) {
        console.error('🚫 Network Error:', error.message)
        console.error('   Backend URL:', API_URL)
        console.error('   Error code:', error.code)
        console.error('   Please ensure the backend server is running on port 8000')
        return Promise.reject(new Error(`Cannot connect to backend server. Please ensure the API is running at ${API_URL}`))
      }
      
      // If it's not a known network error, log it but let it pass through
      console.warn('⚠️ Unknown error (no response):', error.message, error.code)
    }

    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ Request timeout:', originalRequest?.url)
      return Promise.reject(new Error('Request timeout. The server is taking too long to respond.'))
    }

    // Handle network errors with retry
    if (shouldRetry(error)) {
      originalRequest._retryCount = originalRequest._retryCount || 0
      
      if (originalRequest._retryCount < MAX_RETRIES) {
        originalRequest._retryCount++
        await delay(RETRY_DELAY * originalRequest._retryCount) // Exponential backoff
        return apiClient(originalRequest)
      }
    }

    // Handle 401 Unauthorized - Token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request while token is being refreshed
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return apiClient(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      
      if (!refreshToken) {
        // No refresh token, logout
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Try to refresh token
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        })

        const { access_token } = response.data
        localStorage.setItem('access_token', access_token)
        
        // Update authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        
        processQueue(null, access_token)
        isRefreshing = false
        
        // Retry original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout
        processQueue(refreshError as Error, null)
        isRefreshing = false
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

// Convenience methods that return data directly
export const api = {
  get: async (url: string, config?: any) => {
    const response = await apiClient.get(url, config)
    return response.data
  },
  post: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.post(url, data, config)
    return response.data
  },
  put: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.put(url, data, config)
    return response.data
  },
  patch: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.patch(url, data, config)
    return response.data
  },
  delete: async (url: string, config?: any) => {
    const response = await apiClient.delete(url, config)
    return response.data
  },
}
