/**
 * Admin route component that requires admin privileges.
 * Shows 404 page for non-admin users to hide the existence of admin routes.
 */
import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { NotFoundPage } from '@/pages/NotFoundPage'

interface AdminRouteProps {
  children: React.ReactNode
}

export const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return <div>Loading...</div> // TODO: Add proper loading component
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!isAdmin) {
    // Show 404 page instead of redirecting to hide admin routes
    return <NotFoundPage />
  }

  return <>{children}</>
}

