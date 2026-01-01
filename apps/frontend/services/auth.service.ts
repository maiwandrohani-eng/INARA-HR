/**
 * Authentication Service
 * API calls for authentication operations
 */

import apiClient from '@/lib/api-client'

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  roles: string[]
  permissions: string[]
}

interface ApiRole {
  id: string
  name: string
  display_name: string
}

interface ApiUser {
  id: string
  email: string
  first_name: string
  last_name: string
  roles: ApiRole[]
  permissions?: string[]
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log('🔗 Connecting to:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1')
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials)
      
      // Store tokens
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      
      return response.data
    } catch (error: any) {
      // Enhanced error logging
      if (!error.response) {
        console.error('🚫 Network Error - Backend not reachable')
        console.error('   URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1')
        console.error('   Make sure the backend server is running on port 8000')
        throw new Error('Cannot connect to server. Please ensure the backend API is running.')
      }
      throw error
    }
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiUser>('/auth/me')
    
    // Transform API response to match User interface
    // API returns roles as objects with {id, name, display_name}, we need just the names
    return {
      ...response.data,
      roles: response.data.roles.map(role => role.name),
      permissions: response.data.permissions || []
    }
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email', { token })
  }

  async resendVerificationEmail(email: string): Promise<void> {
    await apiClient.post('/auth/resend-verification', { email })
  }
}

export const authService = new AuthService()
