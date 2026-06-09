import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { format } from 'date-fns'
import { NavBar } from '@/components/layout'
import { useAuth } from '@/contexts/AuthContext'
import { useFeedback } from '@/contexts/FeedbackContext'
import { authService } from '@/services/auth'

const profileSchema = z.object({
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters'),
})

type ProfileFormData = z.infer<typeof profileSchema>

export const EditProfilePage: React.FC = () => {
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const { showFeedback } = useFeedback()
  const [email, setEmail] = useState('')
  const [createdAt, setCreatedAt] = useState<string | null>(null)
  const [loadingProfile, setLoadingProfile] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  })

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const user = await authService.getCurrentUser()
        setEmail(user.email)
        setCreatedAt(user.created_at)
        reset({ username: user.username })
      } catch {
        showFeedback('Failed to load profile.', 'error')
      } finally {
        setLoadingProfile(false)
      }
    }

    loadProfile()
  }, [reset, showFeedback])

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setIsSaving(true)
      await authService.updateProfile({ username: data.username.trim() })
      await refreshUser()
      reset({ username: data.username.trim() })
      showFeedback('Profile updated successfully.', 'success')
    } catch (err: any) {
      showFeedback(err.response?.data?.detail || 'Failed to update profile.', 'error')
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
          <h1 className="text-2xl font-bold text-neutral-DEFAULT">Edit Profile</h1>
          <p className="mt-2 text-sm text-neutral-DEFAULT/70">
            Update how your name appears in leagues and rankings.
          </p>

          {loadingProfile ? (
            <p className="mt-6 text-sm text-neutral-DEFAULT/60">Loading profile...</p>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-neutral-DEFAULT">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  disabled
                  className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/20 bg-neutral-light px-3 py-2 text-neutral-DEFAULT/70 cursor-not-allowed"
                />
                <p className="mt-1 text-xs text-neutral-DEFAULT/60">
                  Email changes are not supported yet.
                </p>
              </div>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-neutral-DEFAULT">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  {...register('username')}
                  className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
                )}
              </div>

              {createdAt && (
                <p className="text-xs text-neutral-DEFAULT/60">
                  Member since {format(new Date(createdAt), 'MMM d, yyyy')}
                </p>
              )}

              <button
                type="submit"
                disabled={isSaving || !isDirty}
                className="rounded-md bg-primary-medium px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSaving ? 'Saving...' : 'Save changes'}
              </button>

              <Link
                to="/account"
                className="ml-4 text-sm text-primary-medium hover:text-primary-dark transition-colors"
              >
                Account settings
              </Link>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
