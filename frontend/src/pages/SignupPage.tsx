import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const signupSchema = z
  .object({
    email: z.string().email('Invalid email address'),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(50, 'Username must be less than 50 characters'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

type SignupFormData = z.infer<typeof signupSchema>

export const SignupPage: React.FC = () => {
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const { signup } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  })

  const onSubmit = async (data: SignupFormData) => {
    try {
      setError('')
      setIsLoading(true)
      await signup(data.email, data.password, data.username)
      setSuccess(true)
      // Don't redirect - user should check their email and click the verification link
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
        <div className="max-w-md w-full text-center space-y-4">
          <div className="rounded-md bg-green-50 p-4">
            <h3 className="text-lg font-medium text-green-800">
              Account created successfully! 🎉
            </h3>
            <p className="mt-2 text-sm text-green-700">
              We've sent a verification email to your inbox. Please check your email and click the verification link to activate your account.
            </p>
            <p className="mt-4 text-xs text-green-600">
              Didn't receive the email? Check your spam folder or{' '}
              <Link
                to="/verify-email"
                className="font-medium underline hover:text-green-800"
              >
                click here to resend
              </Link>
            </p>
          </div>
          <div className="mt-4">
            <Link
              to="/login"
              className="text-sm font-medium text-primary-medium hover:text-primary-dark"
            >
              Back to login
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-neutral-DEFAULT">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-neutral-DEFAULT">
            Or{' '}
            <Link
              to="/login"
              className="font-medium text-primary-medium hover:text-primary-dark"
            >
              sign in to your existing account
            </Link>
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
              <label htmlFor="username" className="block text-sm font-medium text-neutral-DEFAULT">
                Username
              </label>
              <input
                {...register('username')}
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
                placeholder="username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-DEFAULT">
                Password
              </label>
              <input
                {...register('password')}
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium sm:text-sm"
                placeholder="Password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
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
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-medium hover:bg-primary-DEFAULT focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

