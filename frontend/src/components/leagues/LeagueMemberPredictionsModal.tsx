import React from 'react'
import { UserPredictionsTable } from '@/components/predictions/UserPredictionsTable'
import { LeagueMemberPredictionsResponse } from '@/services/leagues'

interface LeagueMemberPredictionsModalProps {
  isOpen: boolean
  isLoading: boolean
  error?: string
  username: string
  data?: LeagueMemberPredictionsResponse
  onClose: () => void
}

export const LeagueMemberPredictionsModal: React.FC<LeagueMemberPredictionsModalProps> = ({
  isOpen,
  isLoading,
  error,
  username,
  data,
  onClose,
}) => {
  if (!isOpen) return null

  const displayName = data?.username || username

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl max-h-[85vh] overflow-hidden rounded-lg bg-white shadow-xl flex flex-col"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-neutral-DEFAULT/10 px-6 py-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">
              {displayName}&apos;s predictions
            </h2>
            {data && !isLoading && (
              <div className="mt-2 flex items-center justify-between gap-4">
                <p className="text-sm text-neutral-DEFAULT/70">
                  {data.predictions.length} prediction{data.predictions.length === 1 ? '' : 's'}
                </p>
                <div
                  className="flex shrink-0 items-center gap-1.5 rounded-lg bg-primary-medium/10 px-3 py-1"
                  aria-label={`Total score: ${data.total_points} points`}
                >
                  <svg
                    className="h-5 w-5 text-primary-medium"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                    />
                  </svg>
                  <span className="text-xl font-bold tabular-nums text-primary-medium">
                    {data.total_points} pts
                  </span>
                </div>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-neutral-DEFAULT/60 hover:bg-neutral-light hover:text-neutral-DEFAULT transition-colors"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="overflow-y-auto px-6 py-4">
          {isLoading ? (
            <p className="text-sm text-neutral-DEFAULT/70">Loading predictions...</p>
          ) : error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : data ? (
            <UserPredictionsTable predictions={data.predictions} showMatchDate />
          ) : null}
        </div>
      </div>
    </div>
  )
}
