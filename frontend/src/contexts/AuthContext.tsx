/**
 * Authentication context for managing user state.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, AuthResponse, SignupResponse } from '@/services/auth'

interface User {
  id: string
  email: string
  username: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
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
    const token = localStorage.getItem('access_token')
    if (token) {
      // TODO: Verify token and fetch user data
      // For now, we'll just set loading to false
      setLoading(false)
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response: AuthResponse = await authService.login({ email, password })
    localStorage.setItem('access_token', response.access_token)
    setUser(response.user)
  }

  const signup = async (email: string, password: string, username: string) => {
    const response: SignupResponse = await authService.signup({ email, password, username })
    // Signup doesn't return a token, user needs to verify email first
    // Don't set user or token - redirect to verification page
  }

  const logout = async () => {
    await authService.logout()
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

