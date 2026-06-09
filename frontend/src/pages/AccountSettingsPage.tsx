import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { NavBar } from '@/components/layout'
import { useFeedback } from '@/contexts/FeedbackContext'
import { authService } from '@/services/auth'

const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, 'Current password is required'),
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

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

export const AccountSettingsPage: React.FC = () => {
  const navigate = useNavigate()
  const { showFeedback } = useFeedback()
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  })

  const onSubmit = async (data: ChangePasswordFormData) => {
    try {
      setIsSaving(true)
      await authService.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      })
      reset()
      showFeedback('Password changed successfully.', 'success')
    } catch (err: any) {
      showFeedback(err.response?.data?.detail || 'Failed to change password.', 'error')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="text-sm text-primary-medium hover:text-primary-dark transition-colors"
        >
          ← Back to dashboard
        </button>

        <div className="mt-4 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
          <h1 className="text-2xl font-bold text-neutral-DEFAULT">Account Settings</h1>
          <p className="mt-2 text-sm text-neutral-DEFAULT/70">
            Change your password or manage your account security.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-5">
            <div>
              <label
                htmlFor="current_password"
                className="block text-sm font-medium text-neutral-DEFAULT"
              >
                Current password
              </label>
              <input
                id="current_password"
                type="password"
                autoComplete="current-password"
                {...register('current_password')}
                className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
              />
              {errors.current_password && (
                <p className="mt-1 text-sm text-red-600">{errors.current_password.message}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="new_password"
                className="block text-sm font-medium text-neutral-DEFAULT"
              >
                New password
              </label>
              <input
                id="new_password"
                type="password"
                autoComplete="new-password"
                {...register('new_password')}
                className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
              />
              {errors.new_password && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-neutral-DEFAULT"
              >
                Confirm new password
              </label>
              <input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                {...register('confirmPassword')}
                className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-4">
              <button
                type="submit"
                disabled={isSaving}
                className="rounded-md bg-primary-medium px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSaving ? 'Updating...' : 'Change password'}
              </button>
              <Link
                to="/profile"
                className="text-sm text-primary-medium hover:text-primary-dark transition-colors"
              >
                Edit profile
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
