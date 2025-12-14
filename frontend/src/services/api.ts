/**
 * API client configuration and base setup.
 */
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Use relative URL to go through Vite proxy in development
// In production, this will be set via VITE_API_BASE_URL environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear all auth data and redirect to login
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_data')
      localStorage.removeItem('remember_me')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

