import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { LatestResultsData } from '@/types/matches'
import { getLatestResults } from '@/services/matches'
import { mockLatestResults } from '@/data/mockMatches'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { formatMatchDateLocal } from '@/utils/timezone'

interface LatestResultsProps {
  data?: LatestResultsData // Optional prop for when we integrate with backend
}

export const LatestResults: React.FC<LatestResultsProps> = ({ data: propData }) => {
  // Fetch latest results from API
  const { data: apiData, isLoading } = useQuery<LatestResultsData>({
    queryKey: ['latestResults'],
    queryFn: getLatestResults,
    staleTime: 60 * 1000,
    retry: 1,
  })

  // Use provided data, API data, or fall back to mock data
  const resultsData = propData || apiData || mockLatestResults

  const formatDate = (isoString: string): string => formatMatchDateLocal(isoString)

  if (isLoading) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#FAF0CA' }}>
        <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">Latest Results</h3>
        <p className="text-neutral-DEFAULT/70">Loading...</p>
      </div>
    )
  }

  if (resultsData.matches.length === 0) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#FAF0CA' }}>
        <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">Latest Results</h3>
        <p className="text-neutral-DEFAULT/70">No recent results</p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#FAF0CA' }}>
      <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">Latest Results</h3>

      <div className="space-y-3">
        {resultsData.matches.slice(0, 5).map((match) => (
          <div
            key={match.id}
            className="border border-neutral-DEFAULT/20 rounded-lg p-3 transition-colors"
            style={{ backgroundColor: '#D0C18E' }}
          >
            {/* Match Header */}
            <div className="flex items-center justify-between mb-2">
              {match.group && (
                <span className="text-xs text-neutral-DEFAULT/70 font-medium">
                  Group {match.group.letter}
                </span>
              )}
              <span className="text-xs text-neutral-DEFAULT/60">{formatDate(match.scheduledAt)}</span>
            </div>

            {/* Teams and Score */}
            <div className="flex items-center justify-between">
              {/* Home Team */}
              <div className="flex items-center space-x-2 flex-1">
                <span
                  className={`fi fi-${getCountryCodeForFlag(match.homeTeam.countryCode)} fis`}
                  style={{ fontSize: '1.2rem' }}
                ></span>
                <span className="text-sm font-medium text-neutral-DEFAULT">
                  {abbreviateCountryName(match.homeTeam.name)}
                </span>
              </div>

              {/* Score */}
              <div className="px-4 flex items-center space-x-2">
                <span className="text-lg font-bold text-neutral-DEFAULT">
                  {match.homeScore ?? '-'}
                </span>
                <span className="text-neutral-DEFAULT/50">-</span>
                <span className="text-lg font-bold text-neutral-DEFAULT">
                  {match.awayScore ?? '-'}
                </span>
                {match.homePenaltyScore !== undefined && match.awayPenaltyScore !== undefined && (
                  <span className="text-xs text-neutral-DEFAULT/60 ml-2">
                    ({match.homePenaltyScore}-{match.awayPenaltyScore} pen.)
                  </span>
                )}
              </div>

              {/* Away Team */}
              <div className="flex items-center space-x-2 flex-1 justify-end">
                <span className="text-sm font-medium text-neutral-DEFAULT">
                  {abbreviateCountryName(match.awayTeam.name)}
                </span>
                <span
                  className={`fi fi-${getCountryCodeForFlag(match.awayTeam.countryCode)} fis`}
                  style={{ fontSize: '1.2rem' }}
                ></span>
              </div>
            </div>

            {/* Stadium (optional, smaller text) */}
            {match.stadium && (
              <div className="text-xs text-neutral-DEFAULT/60 mt-2 text-center">
                {match.stadium.name}, {match.stadium.city}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

