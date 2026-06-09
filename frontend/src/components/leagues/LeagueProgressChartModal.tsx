import React, { useEffect, useState } from 'react'
import { LeagueProgressResponse } from '@/services/leagues'
import { LeagueProgressChart, MemberFilter } from './LeagueProgressChart'

interface LeagueProgressChartModalProps {
  isOpen: boolean
  isLoading: boolean
  error?: string
  leagueName: string
  data?: LeagueProgressResponse
  onClose: () => void
}

export const LeagueProgressChartModal: React.FC<LeagueProgressChartModalProps> = ({
  isOpen,
  isLoading,
  error,
  leagueName,
  data,
  onClose,
}) => {
  const [memberFilter, setMemberFilter] = useState<MemberFilter>('all')

  useEffect(() => {
    if (isOpen) {
      setMemberFilter('all')
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) {
      return undefined
    }

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, onClose])

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-neutral-light">
      <header className="flex items-start justify-between gap-4 border-b border-neutral-DEFAULT/10 bg-white px-4 py-4 sm:px-8">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-primary-medium">League progress</p>
          <h2 className="mt-1 text-xl font-bold text-neutral-DEFAULT sm:text-2xl">{leagueName}</h2>
          <p className="mt-1 text-sm text-neutral-DEFAULT/70">
            Cumulative points after each finished match. Use the filter to focus on the top five or view everyone.
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-md p-2 text-neutral-DEFAULT/60 hover:bg-neutral-light hover:text-neutral-DEFAULT transition-colors"
          aria-label="Close league progress chart"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <div className="flex min-h-0 flex-1 flex-col px-4 py-4 sm:px-8 sm:py-6">
        {isLoading ? (
          <div className="flex flex-1 items-center justify-center text-sm text-neutral-DEFAULT/70">
            Loading chart...
          </div>
        ) : error ? (
          <div className="flex flex-1 items-center justify-center">
            <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
          </div>
        ) : !data || !data.has_scored_matches ? (
          <div className="flex flex-1 items-center justify-center">
            <div className="max-w-md rounded-lg border border-dashed border-neutral-DEFAULT/20 bg-white px-6 py-8 text-center">
              <p className="text-base font-medium text-neutral-DEFAULT">No match results yet</p>
              <p className="mt-2 text-sm text-neutral-DEFAULT/70">
                The race chart will come alive once the first match is scored. Check back after kickoff.
              </p>
            </div>
          </div>
        ) : (
          <div className="relative min-h-0 flex-1 rounded-xl border border-neutral-DEFAULT/10 bg-white p-3 shadow-sm sm:p-6">
            <div className="absolute right-3 top-3 z-10 sm:right-6 sm:top-6">
              <div
                className="inline-flex rounded-lg border border-neutral-DEFAULT/15 bg-white p-1 shadow-sm"
                role="group"
                aria-label="Filter players shown in chart"
              >
                {(['all', 'top5'] as const).map((option) => {
                  const isActive = memberFilter === option
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setMemberFilter(option)}
                      className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-primary-medium text-white shadow-sm'
                          : 'text-neutral-DEFAULT/70 hover:bg-neutral-light hover:text-neutral-DEFAULT'
                      }`}
                      aria-pressed={isActive}
                    >
                      {option === 'all' ? 'All' : 'Top 5'}
                    </button>
                  )
                })}
              </div>
            </div>

            <LeagueProgressChart
              data={data}
              variant="fullscreen"
              memberFilter={memberFilter}
              className="h-full min-h-[420px] pt-10 sm:pt-12"
            />
          </div>
        )}
      </div>
    </div>
  )
}
