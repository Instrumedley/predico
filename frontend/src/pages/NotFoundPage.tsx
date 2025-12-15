import React from 'react'
import { Link } from 'react-router-dom'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
      <div className="max-w-md w-full text-center">
        <h1 className="text-9xl font-bold text-neutral-DEFAULT/20">404</h1>
        <h2 className="mt-4 text-3xl font-bold text-neutral-DEFAULT">Page Not Found</h2>
        <p className="mt-4 text-neutral-DEFAULT/70">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-8">
          <Link
            to="/dashboard"
            className="inline-block px-6 py-3 bg-primary-medium text-white rounded-md hover:bg-primary-DEFAULT transition-colors"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

