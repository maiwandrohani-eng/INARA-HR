/**
 * Authentication State Management (Zustand)
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authService, User } from '@/services/auth.service'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User | null) => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          console.log('🔑 Logging in...')
          await authService.login({ email, password })
          console.log('✅ Login successful, fetching user...')
          const user = await authService.getCurrentUser()
          console.log('✅ User fetched:', user)
          console.log('📋 User roles:', user.roles)
          console.log('📋 User permissions:', user.permissions)
          console.log('👑 Is admin?', user.roles?.includes('admin') || user.roles?.includes('ceo') || user.roles?.includes('super_admin'))
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          console.error('❌ Login error:', error)
          // Clear any partial state on error
          set({ user: null, isAuthenticated: false, isLoading: false })
          // Clean up tokens if they were set
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          throw error
        }
      },

      logout: async () => {
        await authService.logout()
        set({ user: null, isAuthenticated: false })
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user })
      },

      fetchUser: async () => {
        if (authService.isAuthenticated()) {
          try {
            const user = await authService.getCurrentUser()
            set({ user, isAuthenticated: true })
          } catch (error) {
            set({ user: null, isAuthenticated: false })
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
