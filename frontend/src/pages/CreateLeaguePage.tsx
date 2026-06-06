import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { NavBar } from '@/components/layout'
import { createLeague } from '@/services/leagues'
import { useFeedback } from '@/contexts/FeedbackContext'

const createLeagueSchema = z
  .object({
    name: z.string().min(1, 'League name is required').max(100),
    description: z.string().max(500).optional(),
    is_private: z.boolean(),
    password: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.is_private && (!data.password || data.password.length < 4)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Password must be at least 4 characters for private leagues',
        path: ['password'],
      })
    }
  })

type CreateLeagueFormData = z.infer<typeof createLeagueSchema>

export const CreateLeaguePage: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showFeedback } = useFeedback()
  const [error, setError] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CreateLeagueFormData>({
    resolver: zodResolver(createLeagueSchema),
    defaultValues: {
      name: '',
      description: '',
      is_private: false,
    },
  })

  const isPrivate = watch('is_private')

  const mutation = useMutation({
    mutationFn: createLeague,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['myLeagues'] })
      queryClient.invalidateQueries({ queryKey: ['allLeagues'] })
      showFeedback(
        data.is_private
          ? `League created. Share the password with friends to let them join.`
          : 'League created successfully.',
        'success'
      )
      navigate('/dashboard')
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail)) {
        setError(detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(', ') || 'Failed to create league')
      } else {
        setError('Failed to create league. Please try again.')
      }
    },
  })

  const onSubmit = (data: CreateLeagueFormData) => {
    setError('')
    mutation.mutate({
      name: data.name.trim(),
      description: data.description?.trim() || undefined,
      is_private: data.is_private,
      password: data.is_private ? data.password : undefined,
    })
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link
          to="/dashboard"
          className="text-sm text-primary-medium hover:text-primary-dark transition-colors"
        >
          ← Back to dashboard
        </Link>

        <h1 className="mt-4 text-2xl font-bold text-neutral-DEFAULT">Create League</h1>
        <p className="mt-2 text-sm text-neutral-DEFAULT/70">
          Start a league for friends or open it to everyone.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          )}

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-neutral-DEFAULT">
              League Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              type="text"
              {...register('name')}
              className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
              placeholder="e.g. Office World Cup 2026"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-neutral-DEFAULT">
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              {...register('description')}
              className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
              placeholder="Optional description for your league"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          <div className="space-y-3">
            <span className="block text-sm font-medium text-neutral-DEFAULT">Visibility</span>
            <div className="flex items-center justify-between rounded-md border border-neutral-DEFAULT/20 p-4">
              <div>
                <p className="text-sm font-medium text-neutral-DEFAULT">
                  {isPrivate ? 'Password protected' : 'Open for everyone'}
                </p>
                <p className="text-xs text-neutral-DEFAULT/60 mt-1">
                  {isPrivate
                    ? 'Only people with the league password can join.'
                    : 'Anyone can find and join this league from the global list.'}
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" {...register('is_private')} />
                <div className="w-11 h-6 bg-neutral-DEFAULT/20 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary-medium rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-DEFAULT/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-medium" />
              </label>
            </div>
          </div>

          {isPrivate && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-DEFAULT">
                League Password <span className="text-red-500">*</span>
              </label>
              <input
                id="password"
                type="password"
                {...register('password')}
                className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
                placeholder="Password for joining"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full rounded-md bg-primary-medium px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Creating...' : 'Create League'}
          </button>
        </form>
      </div>
    </div>
  )
}
