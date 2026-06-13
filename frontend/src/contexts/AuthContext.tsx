/**
 * Authentication context for managing user state.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, AuthResponse } from '@/services/auth'
import {
  clearAuthSession,
  getAccessToken,
  getUserDataRaw,
  setAuthSession,
  updateStoredUserData,
} from '@/utils/authStorage'

interface User {
  id: number
  email: string
  username: string
  is_superuser?: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  signup: (email: string, password: string, username: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
  isAdmin: boolean
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  
  // Refresh user data from backend
  const refreshUser = async () => {
    try {
      const { authService } = await import('@/services/auth')
      const userData = await authService.getCurrentUser()
      setUser(userData)
      updateStoredUserData(userData)
    } catch (error) {
      // If refresh fails, clear auth data
      clearAuthSession()
      setUser(null)
      throw error
    }
  }

  useEffect(() => {
    // Check if user is already logged in
    const restoreAuth = async () => {
      try {
        const token = getAccessToken()
        const storedUser = getUserDataRaw()
        
        if (token && storedUser) {
          try {
            // Restore user from storage
            const userData = JSON.parse(storedUser) as User
            setUser(userData)
            
            // Refresh user data from backend to get latest info (including is_superuser)
            try {
              await refreshUser()
            } catch (error) {
              // If refresh fails, keep cached data but log error
              console.warn('Failed to refresh user data, using cached data')
            }
          } catch (error) {
            // Invalid stored data, clear it
            clearAuthSession()
          }
        }
      } finally {
        setLoading(false)
      }
    }
    
    restoreAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = async (email: string, password: string, rememberMe: boolean = false) => {
    const response: AuthResponse = await authService.login({ email, password, rememberMe })

    setAuthSession(response.access_token, response.user, rememberMe)
    setUser(response.user)
    
    // Refresh user data to get latest info including is_superuser
    try {
      await refreshUser()
    } catch (error) {
      // If refresh fails, use the data from login response
      console.warn('Failed to refresh user data after login')
    }
  }

  const signup = async (email: string, password: string, username: string) => {
    await authService.signup({ email, password, username })
    // Signup doesn't return a token, user needs to verify email first
    // Don't set user or token - redirect to verification page
  }

  const logout = async () => {
    await authService.logout()
    clearAuthSession()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
        isAuthenticated: !!user,
        isAdmin: !!user?.is_superuser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
