import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../services/api'

interface User {
  id: number
  username: string
  email: string
  games_played: number
  games_won: number
  total_points: number
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (username: string, password: string) => Promise<boolean>
  register: (username: string, email: string, password: string) => Promise<boolean>
  logout: () => void
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/auth/login', { username, password })
          const { access_token } = response.data
          
          set({ token: access_token, isAuthenticated: true })
          
          // Fetch user data
          await get().fetchUser()
          
          set({ isLoading: false })
          return true
        } catch (err: any) {
          set({ 
            isLoading: false, 
            error: err.response?.data?.detail || 'Login failed'
          })
          return false
        }
      },
      
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          await api.post('/auth/register', { username, email, password })
          
          // Auto-login after registration
          return await get().login(username, password)
        } catch (err: any) {
          set({ 
            isLoading: false, 
            error: err.response?.data?.detail || 'Registration failed'
          })
          return false
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        })
      },
      
      fetchUser: async () => {
        const { token } = get()
        if (!token) return
        
        try {
          const response = await api.get('/auth/me')
          set({ user: response.data })
        } catch (err) {
          // Token might be expired
          get().logout()
        }
      },
      
      clearError: () => set({ error: null })
    }),
    {
      name: 'teyuna-auth',
      partialize: (state) => ({ 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
)

