import React, { useEffect, useState } from 'react'
import { LeagueProgressResponse } from '@/services/leagues'
import { LeagueProgressChart } from './LeagueProgressChart'
import { LeagueProgressMatrix } from './LeagueProgressMatrix'
import { ProgressViewMode } from './leagueProgressViews'

const PREVIEW_CHART_DURATION_MS = 5000
const PREVIEW_CROSSFADE_MS = 700

interface LeagueProgressChartPreviewProps {
  isLoading: boolean
  error?: string
  data?: LeagueProgressResponse
  onExpand: (viewMode: ProgressViewMode) => void
}

export const LeagueProgressChartPreview: React.FC<LeagueProgressChartPreviewProps> = ({
  isLoading,
  error,
  data,
  onExpand,
}) => {
  const [showMatrix, setShowMatrix] = useState(false)

  useEffect(() => {
    setShowMatrix(false)
    if (!data?.has_scored_matches) {
      return undefined
    }

    const interval = window.setInterval(() => {
      setShowMatrix((current) => !current)
    }, PREVIEW_CHART_DURATION_MS)

    return () => window.clearInterval(interval)
  }, [data])

  const activeView: ProgressViewMode = showMatrix ? 'matrix' : 'chart'

  return (
    <div className="mt-8 overflow-hidden rounded-lg border border-neutral-DEFAULT/20 bg-white shadow-sm">
      <div className="border-b border-neutral-DEFAULT/10 bg-neutral-light px-4 py-3 sm:px-6">
        <h2 className="text-sm font-semibold text-neutral-DEFAULT">League progress</h2>
      </div>

      {isLoading ? (
        <div className="flex h-[360px] items-center justify-center text-sm text-neutral-DEFAULT/70">
          Loading chart...
        </div>
      ) : error ? (
        <div className="flex h-[360px] items-center justify-center px-6">
          <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        </div>
      ) : !data?.has_scored_matches ? (
        <div className="flex h-[360px] items-center justify-center px-6">
          <div className="max-w-md text-center">
            <p className="text-sm font-medium text-neutral-DEFAULT">No match results yet</p>
            <p className="mt-2 text-xs text-neutral-DEFAULT/70">
              The progress views will appear here once the first match is scored.
            </p>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => onExpand(activeView)}
          className="group relative block w-full cursor-pointer text-left transition-shadow hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-medium focus-visible:ring-offset-2"
          aria-label={`Open league progress ${activeView === 'chart' ? 'chart' : 'matrix'} full screen`}
        >
          <div className="relative h-[360px] px-2 pb-2 pt-3 sm:px-4 sm:pb-4">
            <div
              className={`absolute inset-0 px-2 pb-2 pt-3 transition-opacity duration-700 sm:px-4 sm:pb-4 ${
                showMatrix ? 'pointer-events-none opacity-0' : 'opacity-100'
              }`}
              style={{ transitionDuration: `${PREVIEW_CROSSFADE_MS}ms` }}
            >
              <LeagueProgressChart data={data} variant="preview" className="h-full w-full" />
            </div>

            <div
              className={`absolute inset-0 px-2 pb-2 pt-3 transition-opacity duration-700 sm:px-4 sm:pb-4 ${
                showMatrix ? 'opacity-100' : 'pointer-events-none opacity-0'
              }`}
              style={{ transitionDuration: `${PREVIEW_CROSSFADE_MS}ms` }}
            >
              <LeagueProgressMatrix data={data} variant="preview" className="h-full w-full" />
            </div>
          </div>

          <div className="pointer-events-none absolute inset-0 flex items-end justify-end bg-gradient-to-t from-black/10 via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100">
            <span className="m-4 inline-flex items-center gap-2 rounded-full bg-white/95 px-3 py-1.5 text-xs font-medium text-neutral-DEFAULT shadow-sm backdrop-blur-sm">
              <svg className="h-4 w-4 text-primary-medium" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                />
              </svg>
              Click to expand
            </span>
          </div>
        </button>
      )}
    </div>
  )
}
