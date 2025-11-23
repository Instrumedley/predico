/**
 * Authentication service.
 */
import apiClient from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  email: string
  password: string
  username: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    username: string
  }
}

export interface SignupResponse {
  user: {
    id: number
    email: string
    username: string
    is_active: boolean
    email_verified: boolean
    created_at: string
  }
  message: string
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', credentials)
    return response.data
  },

  async signup(data: SignupData): Promise<SignupResponse> {
    const response = await apiClient.post<SignupResponse>('/api/v1/auth/signup', data)
    return response.data
  },

  async logout(): Promise<void> {
    // Clear token from localStorage
    localStorage.removeItem('access_token')
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/api/v1/auth/verify-email', { token })
    return response.data
  },

  async resendVerification(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/api/v1/auth/resend-verification', { email })
    return response.data
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/api/v1/auth/forgot-password', { email })
    return response.data
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/api/v1/auth/reset-password', {
      token,
      new_password: newPassword,
    })
    return response.data
  },
}


