import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import apiClient from '@/services/api'

const forgotPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

export const ForgotPasswordPage: React.FC = () => {
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      setError('')
      await apiClient.post('/api/v1/auth/forgot-password', { email: data.email })
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.')
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-neutral-DEFAULT">Check Your Email</h2>
          </div>
          <div className="rounded-md bg-green-50 p-4">
            <div className="text-sm text-green-800">
              <p className="font-medium">
                If an account exists with that email, a password reset link has been sent.
              </p>
              <p className="mt-2">Please check your inbox and follow the instructions.</p>
            </div>
          </div>
          <div className="text-center">
            <Link
              to="/login"
              className="font-medium text-primary-medium hover:text-primary-dark"
            >
              Back to login
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-neutral-DEFAULT">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-neutral-DEFAULT">
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-neutral-DEFAULT">
              Email address
            </label>
            <input
              {...register('email')}
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              className="mt-1 appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
              placeholder="you@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-DEFAULT hover:bg-primary-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-medium"
            >
              Send reset link
            </button>
          </div>

          <div className="text-center">
            <Link
              to="/login"
              className="font-medium text-primary-medium hover:text-primary-dark"
            >
              Back to login
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

