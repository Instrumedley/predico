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
          <div>
            <h2 className="text-lg font-semibold text-neutral-DEFAULT">
              {displayName}&apos;s predictions
            </h2>
            {data && !isLoading && (
              <p className="mt-1 text-sm text-neutral-DEFAULT/70">
                {data.predictions.length} prediction{data.predictions.length === 1 ? '' : 's'} ·{' '}
                {data.total_points} pts
              </p>
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
