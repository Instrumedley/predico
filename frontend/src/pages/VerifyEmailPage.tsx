import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import apiClient from '@/services/api'
import { buildLoginPath, getAuthRedirect } from '@/utils/authRedirect'

export const VerifyEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState<string>('')
  const [email, setEmail] = useState<string>('')

  useEffect(() => {
    const token = searchParams.get('token')
    const emailFromState = location.state?.email

    if (emailFromState) {
      setEmail(emailFromState)
    }

    if (token) {
      verifyEmail(token)
    } else {
      // No token - user probably came here directly or from signup page
      // Show a helpful message instead of an error
      setStatus('error')
      setMessage('Please check your email and click the verification link we sent you.')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Only run once on mount to prevent duplicate requests

  const verifyEmail = async (token: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/verify-email', { token })
      setStatus('success')
      setMessage(response.data.message || 'Email verified successfully!')
      setTimeout(() => {
        const redirect = getAuthRedirect()
        navigate(buildLoginPath(redirect))
      }, 3000)
    } catch (error: any) {
      setStatus('error')
      setMessage(
        error.response?.data?.detail || 'Verification failed. The link may be invalid or expired.'
      )
    }
  }

  const resendVerification = async () => {
    if (!email) {
      setMessage('Please enter your email address')
      return
    }

    try {
      await apiClient.post('/api/v1/auth/resend-verification', { email })
      setMessage('Verification email sent! Please check your inbox.')
    } catch (error: any) {
      setMessage(
        error.response?.data?.detail || 'Failed to resend verification email. Please try again.'
      )
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-neutral-DEFAULT">Verify Your Email</h2>
        </div>

        {status === 'verifying' && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-DEFAULT mx-auto"></div>
            <p className="mt-4 text-neutral-DEFAULT">Verifying your email...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="rounded-md bg-green-50 p-4">
            <div className="text-sm text-green-800">
              <p className="font-medium">{message}</p>
              <p className="mt-2">Redirecting to login page...</p>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <div className="rounded-md bg-blue-50 p-4">
              <div className="text-sm text-blue-800">
                <p className="font-medium">{message}</p>
                <p className="mt-2 text-xs">
                  The verification link should be in the email we sent you. Make sure to check your spam folder!
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-neutral-DEFAULT">
                Email address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
                placeholder="you@example.com"
              />
              <button
                onClick={resendVerification}
                className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-medium hover:bg-primary-DEFAULT focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-medium"
              >
                Resend Verification Email
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

