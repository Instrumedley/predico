import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

export const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-neutral-light">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center min-h-screen text-center">
          <h1 className="text-5xl font-extrabold text-neutral-DEFAULT mb-4">
            Welcome to Predico
          </h1>
          <p className="text-xl text-neutral-DEFAULT mb-8">
            Predict World Cup matches and compete with friends!
          </p>
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-medium hover:bg-primary-DEFAULT"
            >
              Go to Dashboard
            </Link>
          ) : (
            <div className="space-x-4">
              <Link
                to="/login"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-medium hover:bg-primary-DEFAULT"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="inline-flex items-center px-6 py-3 border border-primary-medium text-base font-medium rounded-md text-primary-medium bg-white hover:bg-neutral-light"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

