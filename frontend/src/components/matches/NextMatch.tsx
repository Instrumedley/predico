import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { NextMatchData } from '@/types/matches'
import { getNextMatch } from '@/services/matches'
import { mockNextMatch } from '@/data/mockMatches'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'

interface NextMatchProps {
  data?: NextMatchData // Optional prop for when we integrate with backend
}

export const NextMatch: React.FC<NextMatchProps> = ({ data: propData }) => {
  // Fetch next match from API
  const { data: apiData, isLoading } = useQuery<NextMatchData>({
    queryKey: ['nextMatch'],
    queryFn: getNextMatch,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 1,
  })

  // Use provided data, API data, or fall back to mock data
  const matchData = propData || apiData || mockNextMatch

  const formatDateTime = (isoString: string): { date: string; time: string } => {
    const date = new Date(isoString)
    const dateStr = date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    })
    const timeStr = date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    })
    return { date: dateStr, time: timeStr }
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
        <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">Next Match</h3>
        <p className="text-neutral-DEFAULT/70">Loading...</p>
      </div>
    )
  }

  if (matchData.matches.length === 0) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
        <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">Next Match</h3>
        <p className="text-neutral-DEFAULT/70">No upcoming matches</p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
      <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">
        {matchData.matches.length === 1 ? 'Next Match' : 'Next Matches'}
      </h3>

      <div className={`space-y-4 p-4 rounded-lg ${matchData.matches.length === 2 ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : ''}`} style={{ backgroundColor: '#F7FFF6' }}>
        {matchData.matches.map((match) => {
          const { date, time } = formatDateTime(match.scheduledAt)

          return (
            <div key={match.id} className="border border-neutral-DEFAULT/20 rounded-lg p-4">
              {/* Match Info Header */}
              <div className="text-center mb-4">
                {match.group && (
                  <span className="text-xs text-neutral-DEFAULT/70 font-medium">
                    Group {match.group.letter}
                  </span>
                )}
                {match.round && (
                  <div className="text-xs text-neutral-DEFAULT/70 mt-1">
                    {match.round.name}
                  </div>
                )}
              </div>

              {/* Teams */}
              <div className="flex items-center justify-between mb-4">
                {/* Home Team */}
                <div className="flex-1 flex items-center space-x-2">
                  <span
                    className={`fi fi-${getCountryCodeForFlag(match.homeTeam.countryCode)} fis`}
                    style={{ fontSize: '1.5rem' }}
                  ></span>
                  <span className="text-sm font-medium text-neutral-DEFAULT">
                    {abbreviateCountryName(match.homeTeam.name)}
                  </span>
                </div>

                {/* VS */}
                <div className="px-4 text-neutral-DEFAULT/50 font-bold">VS</div>

                {/* Away Team */}
                <div className="flex-1 flex items-center space-x-2 justify-end">
                  <span className="text-sm font-medium text-neutral-DEFAULT">
                    {abbreviateCountryName(match.awayTeam.name)}
                  </span>
                  <span
                    className={`fi fi-${getCountryCodeForFlag(match.awayTeam.countryCode)} fis`}
                    style={{ fontSize: '1.5rem' }}
                  ></span>
                </div>
              </div>

              {/* Date & Time */}
              <div className="text-center border-t border-neutral-DEFAULT/20 pt-3">
                <div className="text-sm font-medium text-neutral-DEFAULT">{date}</div>
                <div className="text-xs text-neutral-DEFAULT/70 mt-1">{time}</div>
                {match.stadium && (
                  <div className="text-xs text-neutral-DEFAULT/60 mt-2">
                    {match.stadium.name}, {match.stadium.city}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

