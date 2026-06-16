import React from 'react'
import { Link } from 'react-router-dom'
import { DASHBOARD_NEWS_ITEMS } from '@/data/dashboardNews'

export const UpdateNewsBanner: React.FC = () => {
  if (DASHBOARD_NEWS_ITEMS.length === 0) {
    return null
  }

  return (
    <div className="mb-2 space-y-3">
      {DASHBOARD_NEWS_ITEMS.map((item) => (
        <div
          key={item.id}
          className="rounded-lg border border-[#B31B1B]/20 px-4 py-3 shadow-sm"
          style={{ backgroundColor: '#FFE4E1', color: '#B31B1B' }}
          role="status"
          aria-live="polite"
        >
          <div className="flex gap-3">
            <div
              className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#B31B1B]/10"
              style={{ color: '#B31B1B' }}
              aria-hidden="true"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>

            <div className="min-w-0 flex-1 text-sm leading-relaxed">
              <p>
                <span className="font-semibold">Update: </span>
                {item.message}
              </p>
              {item.link && (
                <Link
                  to={item.link.href}
                  className="mt-1 inline-block font-medium underline-offset-2 hover:underline"
                  style={{ color: '#B31B1B' }}
                >
                  {item.link.label}
                </Link>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
