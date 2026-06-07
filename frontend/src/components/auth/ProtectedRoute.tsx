/**
 * Protected route component that requires authentication.
 */
import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { buildLoginPath, saveAuthRedirect } from '@/utils/authRedirect'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    const returnPath = `${location.pathname}${location.search}`
    saveAuthRedirect(returnPath)
    return <Navigate to={buildLoginPath(returnPath)} replace />
  }

  return <>{children}</>
}
