import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import apiClient from '@/services/api'

const resetPasswordSchema = z
  .object({
    new_password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.new_password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState(false)
  const [token, setToken] = useState<string>('')

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('Invalid reset link. No token provided.')
    } else {
      setToken(tokenParam)
    }
  }, [searchParams])

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  })

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError('Invalid reset token')
      return
    }

    try {
      setError('')
      await apiClient.post('/auth/reset-password', {
        token,
        new_password: data.new_password,
      })
      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.')
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-neutral-DEFAULT">Password Reset</h2>
          </div>
          <div className="rounded-md bg-green-50 p-4">
            <div className="text-sm text-green-800">
              <p className="font-medium">Password reset successfully!</p>
              <p className="mt-2">Redirecting to login page...</p>
            </div>
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
            Enter your new password below
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label
                htmlFor="new_password"
                className="block text-sm font-medium text-neutral-DEFAULT"
              >
                New Password
              </label>
              <input
                {...register('new_password')}
                id="new_password"
                name="new_password"
                type="password"
                autoComplete="new-password"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
                placeholder="New password"
              />
              {errors.new_password && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
              )}
              <p className="mt-1 text-xs text-neutral-DEFAULT">
                Must be at least 8 characters with uppercase, lowercase, and number
              </p>
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-neutral-DEFAULT"
              >
                Confirm Password
              </label>
              <input
                {...register('confirmPassword')}
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
                placeholder="Confirm password"
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-DEFAULT hover:bg-primary-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-medium"
            >
              Reset Password
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

