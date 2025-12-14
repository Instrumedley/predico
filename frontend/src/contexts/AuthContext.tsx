/**
 * Authentication context for managing user state.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, AuthResponse, SignupResponse } from '@/services/auth'

interface User {
  id: number
  email: string
  username: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  signup: (email: string, password: string, username: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const restoreAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const storedUser = localStorage.getItem('user_data')
        
        if (token && storedUser) {
          try {
            // Restore user from localStorage
            const userData = JSON.parse(storedUser) as User
            setUser(userData)
            
            // Optionally verify token with backend (for now we trust localStorage)
            // If token is invalid, the API interceptor will handle it
          } catch (error) {
            // Invalid stored data, clear it
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_data')
          }
        }
      } finally {
        setLoading(false)
      }
    }
    
    restoreAuth()
  }, [])

  const login = async (email: string, password: string, rememberMe: boolean = false) => {
    const response: AuthResponse = await authService.login({ email, password })
    
    // Always store token and user data in localStorage for persistence on refresh
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('user_data', JSON.stringify(response.user))
    
    // Store rememberMe preference (can be used for future features like longer token expiration)
    if (rememberMe) {
      localStorage.setItem('remember_me', 'true')
    } else {
      localStorage.removeItem('remember_me')
    }
    
    setUser(response.user)
  }

  const signup = async (email: string, password: string, username: string) => {
    const response: SignupResponse = await authService.signup({ email, password, username })
    // Signup doesn't return a token, user needs to verify email first
    // Don't set user or token - redirect to verification page
  }

  const logout = async () => {
    await authService.logout()
    // Clear all auth-related data
    localStorage.removeItem('user_data')
    localStorage.removeItem('remember_me')
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

