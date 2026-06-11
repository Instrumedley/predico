import React, { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { NextMatchData, Match } from '@/types/matches'
import { getNextMatch } from '@/services/matches'
import { getUserPredictions, Prediction } from '@/services/predictions'
import { mockNextMatch } from '@/data/mockMatches'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { formatMatchKickoffLocal, isPredictionLocked } from '@/utils/timezone'

interface NextMatchProps {
  data?: NextMatchData // Optional prop for when we integrate with backend
}

interface NextMatchPredictionStatusProps {
  match: Match
  prediction?: Prediction
  align?: 'end' | 'start'
}

const NextMatchPredictionStatus: React.FC<NextMatchPredictionStatusProps> = ({
  match,
  prediction,
  align = 'end',
}) => {
  const alignmentClass = align === 'end' ? 'sm:text-right sm:justify-end' : 'sm:text-left sm:justify-start'

  if (prediction) {
    return (
      <div className={`flex flex-wrap items-center gap-x-1.5 gap-y-1 text-xs text-neutral-DEFAULT/80 ${alignmentClass}`}>
        <span className="font-medium text-neutral-DEFAULT/70">Your prediction:</span>
        <span
          className={`fi fi-${getCountryCodeForFlag(match.homeTeam.countryCode)} fis`}
          style={{ fontSize: '0.875rem' }}
          aria-hidden="true"
        />
        <span className="font-semibold text-neutral-DEFAULT">
          {prediction.predictedHomeScore} - {prediction.predictedAwayScore}
        </span>
        <span
          className={`fi fi-${getCountryCodeForFlag(match.awayTeam.countryCode)} fis`}
          style={{ fontSize: '0.875rem' }}
          aria-hidden="true"
        />
      </div>
    )
  }

  if (isPredictionLocked(match)) {
    return (
      <div className={`flex items-center gap-1.5 text-xs text-neutral-DEFAULT/70 ${alignmentClass}`}>
        <span aria-hidden="true">😢</span>
        <span>You missed entering your prediction</span>
      </div>
    )
  }

  return (
    <div className={`flex items-start gap-1.5 text-xs text-amber-800 ${alignmentClass}`}>
      <svg
        className="mt-0.5 h-4 w-4 shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <span>
        No prediction yet.{' '}
        <Link
          to={`/scorecard?game=${match.id}`}
          className="font-medium text-amber-900 underline hover:text-amber-950"
        >
          Enter it on the scorecard
        </Link>
      </span>
    </div>
  )
}

export const NextMatch: React.FC<NextMatchProps> = ({ data: propData }) => {
  // Fetch next match from API
  const { data: apiData, isLoading } = useQuery<NextMatchData>({
    queryKey: ['nextMatch'],
    queryFn: getNextMatch,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 1,
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['userPredictions'],
    queryFn: getUserPredictions,
    staleTime: 30 * 1000,
  })

  const predictionsMap = useMemo(() => {
    const map = new Map<number, Prediction>()
    predictions.forEach((prediction) => {
      map.set(prediction.gameId, prediction)
    })
    return map
  }, [predictions])

  // Use provided data, API data, or fall back to mock data
  const matchData = propData || apiData || mockNextMatch
  const singleMatch = matchData.matches.length === 1 ? matchData.matches[0] : null

  if (isLoading) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
        <div className="mb-4 flex items-start justify-between gap-3">
          <h3 className="text-lg font-bold text-neutral-DEFAULT">Next Match</h3>
        </div>
        <p className="text-neutral-DEFAULT/70">Loading...</p>
      </div>
    )
  }

  if (matchData.matches.length === 0) {
    return (
      <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
        <div className="mb-4 flex items-start justify-between gap-3">
          <h3 className="text-lg font-bold text-neutral-DEFAULT">Next Match</h3>
        </div>
        <p className="text-neutral-DEFAULT/70">No upcoming matches</p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6" style={{ backgroundColor: '#EEF8FF' }}>
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <h3 className="text-lg font-bold text-neutral-DEFAULT">
          {matchData.matches.length === 1 ? 'Next Match' : 'Next Matches'}
        </h3>
        {singleMatch && (
          <NextMatchPredictionStatus
            match={singleMatch}
            prediction={predictionsMap.get(singleMatch.id)}
          />
        )}
      </div>

      <div className={`space-y-4 p-4 rounded-lg ${matchData.matches.length === 2 ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : ''}`} style={{ backgroundColor: '#F7FFF6' }}>
        {matchData.matches.map((match) => {
          const kickoff = formatMatchKickoffLocal(match)
          const date = kickoff?.date ?? ''
          const time = kickoff?.time ?? ''

          return (
            <div key={match.id} className="border border-neutral-DEFAULT/20 rounded-lg p-4">
              {matchData.matches.length > 1 && (
                <div className="mb-3 border-b border-neutral-DEFAULT/10 pb-3">
                  <NextMatchPredictionStatus
                    match={match}
                    prediction={predictionsMap.get(match.id)}
                    align="start"
                  />
                </div>
              )}

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

