import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { buildSignupPath, consumeAuthRedirect, saveAuthRedirect } from '@/utils/authRedirect'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional().default(false),
})

type LoginFormData = z.infer<typeof loginSchema>

export const LoginPage: React.FC = () => {
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const { login, isAuthenticated, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirectParam = searchParams.get('redirect')
  const signupPath = buildSignupPath(redirectParam)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  })

  useEffect(() => {
    if (redirectParam) {
      saveAuthRedirect(redirectParam)
    }
  }, [redirectParam])

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate(consumeAuthRedirect(redirectParam || '/dashboard'), { replace: true })
    }
  }, [isAuthenticated, authLoading, navigate, redirectParam])

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-light">
        <div className="text-neutral-DEFAULT">Loading...</div>
      </div>
    )
  }

  // Don't render login form if already authenticated (will redirect)
  if (isAuthenticated) {
    return null
  }

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError('')
      setIsLoading(true)
      await login(data.email, data.password, data.rememberMe)
      navigate(consumeAuthRedirect(redirectParam || '/dashboard'), { replace: true })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-neutral-DEFAULT">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-neutral-DEFAULT">
            Or{' '}
            <Link
              to={signupPath}
              className="font-medium text-primary-medium hover:text-primary-dark"
            >
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                {...register('email')}
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-t-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                {...register('password')}
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-neutral-DEFAULT placeholder-neutral-DEFAULT text-neutral-DEFAULT rounded-b-md focus:outline-none focus:ring-primary-medium focus:border-primary-medium focus:z-10 sm:text-sm"
                placeholder="Password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                {...register('rememberMe')}
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                className="h-4 w-4 text-primary-medium focus:ring-primary-medium border-neutral-DEFAULT rounded"
              />
              <label htmlFor="rememberMe" className="ml-2 block text-sm text-neutral-DEFAULT">
                Remember me
              </label>
            </div>
            <div className="text-sm">
              <Link
                to="/forgot-password"
                className="font-medium text-primary-medium hover:text-primary-dark"
              >
                Forgot your password?
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-medium hover:bg-primary-DEFAULT focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

