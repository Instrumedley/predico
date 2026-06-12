import React, { useState } from 'react'
import { Match } from '@/types/matches'
import { Prediction } from '@/services/predictions'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { abbreviateCountryName } from '@/utils/countryNames'
import { formatMatchKickoffLocal, isPredictionLocked } from '@/utils/timezone'
import { getPredictionRowColors, PREDICTION_MAX_POINTS } from '@/utils/predictions'

interface PredictionRowCardProps {
  match: Match
  prediction?: Prediction | null
  onPredictionSubmit?: (gameId: number, homeScore: number, awayScore: number) => void
  onPredictionChange?: (gameId: number, homeScore: number, awayScore: number) => void
  isSubmitting?: boolean
}

export const PredictionRowCard: React.FC<PredictionRowCardProps> = ({
  match,
  prediction,
  onPredictionSubmit,
  onPredictionChange,
  isSubmitting = false,
}) => {
  const [homeScore, setHomeScore] = useState<string>(
    prediction?.predictedHomeScore?.toString() || ''
  )
  const [awayScore, setAwayScore] = useState<string>(
    prediction?.predictedAwayScore?.toString() || ''
  )
  const [isHomeInputActive, setIsHomeInputActive] = useState(false)
  const [isAwayInputActive, setIsAwayInputActive] = useState(false)
  const homeInputRef = React.useRef<HTMLInputElement>(null)
  const awayInputRef = React.useRef<HTMLInputElement>(null)

  // Update local state when prediction prop changes
  React.useEffect(() => {
    if (prediction) {
      setHomeScore(prediction.predictedHomeScore.toString())
      setAwayScore(prediction.predictedAwayScore.toString())
    }
  }, [prediction])

  // Focus input when it becomes active
  React.useEffect(() => {
    if (isHomeInputActive && homeInputRef.current) {
      homeInputRef.current.focus()
    }
  }, [isHomeInputActive])

  React.useEffect(() => {
    if (isAwayInputActive && awayInputRef.current) {
      awayInputRef.current.focus()
    }
  }, [isAwayInputActive])

  const isFinalized = match.status === 'finished'
  const isLocked = isPredictionLocked(match)
  const hasPrediction = prediction !== null && prediction !== undefined

  const formatDate = (dateString?: string): string => {
    if (!dateString) return ''
    return formatMatchDateLocal(dateString)
  }

  const getMatchStatus = (): string => {
    if (isFinalized) return 'FINALIZED'
    if (isLocked) return 'LOCKED'
    return 'UPCOMING'
  }

  const handleHomeScoreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (value === '' || (/^\d+$/.test(value) && parseInt(value) >= 0 && parseInt(value) <= 20)) {
      setHomeScore(value)
      if (onPredictionChange && value !== '' && awayScore !== '') {
        onPredictionChange(match.id, parseInt(value) || 0, parseInt(awayScore) || 0)
      }
    }
  }

  const handleAwayScoreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    if (value === '' || (/^\d+$/.test(value) && parseInt(value) >= 0 && parseInt(value) <= 20)) {
      setAwayScore(value)
      if (onPredictionChange && value !== '' && homeScore !== '') {
        onPredictionChange(match.id, parseInt(homeScore) || 0, parseInt(value) || 0)
      }
    }
  }

  const handleSubmit = () => {
    const home = parseInt(homeScore) || 0
    const away = parseInt(awayScore) || 0
    if (onPredictionSubmit && !isSubmitting) {
      onPredictionSubmit(match.id, home, away)
    }
  }

  const canSubmit = homeScore !== '' && awayScore !== '' && !isSubmitting && !isLocked && !isFinalized

  // Determine styling for finalized matches
  const getFinalizedCardStyle = () => {
    if (!isFinalized) {
      return { backgroundColor: 'white', color: 'inherit' }
    }

    return getPredictionRowColors(match.status, prediction?.points ?? 0, hasPrediction)
  }

  const cardStyle = getFinalizedCardStyle()
  
  // Helper to get text color class - use parent color for finalized matches
  const getTextColorClass = (defaultClass: string) => {
    return isFinalized ? '' : defaultClass
  }
  
  // Get border color for finalized matches
  const getBorderClass = () => {
    if (!isFinalized) return 'border-neutral-DEFAULT/20'
    const userPoints = prediction?.points ?? 0
    if (userPoints === PREDICTION_MAX_POINTS) {
      return 'border-darkgreen/50'
    }
    if (userPoints === 0) {
      return 'border-neutral-DEFAULT/30'
    }
    return 'border-navajowhite/50'
  }

  const kickoffDisplay = formatMatchKickoffLocal(match)

  return (
    <div
      className={`rounded-lg border shadow-sm p-3 ${getBorderClass()}`}
      style={cardStyle}
    >
      {/* Group Label Row */}
      {match.group && (
        <div className="mb-2 pb-2 border-b border-neutral-DEFAULT/20">
          <span className={`text-sm font-medium ${getTextColorClass('text-neutral-DEFAULT/70')}`}>
            Group {match.group.letter}
          </span>
        </div>
      )}

      {/* Top Row: Team Names and Score/Prediction Inputs */}
      <div className="flex items-center justify-between mb-2">
        {/* Home Team Name */}
        <div className="flex-1 text-left">
          <span className={`font-bold uppercase text-sm ${getTextColorClass('text-neutral-DEFAULT')}`}>
            {abbreviateCountryName(match.homeTeam.name)}
          </span>
        </div>

        {/* Middle: Score or Prediction Inputs */}
        <div className="flex items-center space-x-2 px-4">
          {isFinalized ? (
            // Show actual score for finalized matches
            <div className="bg-primary-medium rounded-lg px-4 py-2">
              <span className="text-white font-bold text-lg">
                {match.homeScore ?? 0} - {match.awayScore ?? 0}
              </span>
            </div>
          ) : (
            // Show prediction inputs for open matches
            <div className="flex items-center space-x-2">
              {!isHomeInputActive ? (
                <button
                  onClick={() => !isLocked && setIsHomeInputActive(true)}
                  onFocus={() => !isLocked && setIsHomeInputActive(true)}
                  tabIndex={isLocked ? -1 : 0}
                  disabled={isLocked}
                  className={`w-12 h-12 border-2 border-neutral-DEFAULT/30 rounded-lg flex items-center justify-center transition-colors bg-white focus:outline-none focus:ring-2 focus:ring-primary-medium ${
                    isLocked ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-medium'
                  }`}
                >
                  {homeScore ? (
                    <span className="text-neutral-DEFAULT font-bold text-lg">{homeScore}</span>
                  ) : (
                    <span className="text-neutral-DEFAULT/60 text-xl font-bold">?</span>
                  )}
                </button>
              ) : (
                <input
                  ref={homeInputRef}
                  type="text"
                  inputMode="numeric"
                  value={homeScore}
                  onChange={handleHomeScoreChange}
                  onBlur={() => {
                    if (homeScore === '') setIsHomeInputActive(false)
                  }}
                  className="w-12 h-12 border-2 border-primary-medium rounded-lg text-center text-lg font-bold text-neutral-DEFAULT focus:outline-none focus:ring-2 focus:ring-primary-medium"
                  maxLength={2}
                />
              )}
              <span className="text-neutral-DEFAULT/50 font-bold">-</span>
              {!isAwayInputActive ? (
                <button
                  onClick={() => !isLocked && setIsAwayInputActive(true)}
                  onFocus={() => !isLocked && setIsAwayInputActive(true)}
                  tabIndex={isLocked ? -1 : 0}
                  disabled={isLocked}
                  className={`w-12 h-12 border-2 border-neutral-DEFAULT/30 rounded-lg flex items-center justify-center transition-colors bg-white focus:outline-none focus:ring-2 focus:ring-primary-medium ${
                    isLocked ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-medium'
                  }`}
                >
                  {awayScore ? (
                    <span className="text-neutral-DEFAULT font-bold text-lg">{awayScore}</span>
                  ) : (
                    <span className="text-neutral-DEFAULT/60 text-xl font-bold">?</span>
                  )}
                </button>
              ) : (
                <input
                  ref={awayInputRef}
                  type="text"
                  inputMode="numeric"
                  value={awayScore}
                  onChange={handleAwayScoreChange}
                  onBlur={() => {
                    if (awayScore === '') setIsAwayInputActive(false)
                  }}
                  className="w-12 h-12 border-2 border-primary-medium rounded-lg text-center text-lg font-bold text-neutral-DEFAULT focus:outline-none focus:ring-2 focus:ring-primary-medium"
                  maxLength={2}
                />
              )}
            </div>
          )}
        </div>

        {/* Away Team Name */}
        <div className="flex-1 text-right">
          <span className={`font-bold uppercase text-sm ${getTextColorClass('text-neutral-DEFAULT')}`}>
            {abbreviateCountryName(match.awayTeam.name)}
          </span>
        </div>
      </div>

      {/* Middle Row: Flags and Predictions */}
      <div className="flex items-center justify-center space-x-4 mb-2 py-2">
        {/* Home Team Flag */}
        <div className="flex flex-col items-center space-y-2">
          <span
            className={`fi fi-${getCountryCodeForFlag(match.homeTeam.countryCode)} fis`}
            style={{ fontSize: '3.5rem' }}
          ></span>
          <span className={`text-lg font-bold ${getTextColorClass('text-neutral-DEFAULT')}`}>
            {isFinalized
              ? hasPrediction
                ? prediction.predictedHomeScore
                : '-'
              : homeScore !== ''
              ? homeScore
              : hasPrediction
              ? prediction.predictedHomeScore
              : '-'}
          </span>
        </div>

        {/* VS */}
        <div className="flex flex-col items-center space-y-2">
          <span className={`font-bold text-xl ${getTextColorClass('text-neutral-DEFAULT/50')}`}>VS</span>
        </div>

        {/* Away Team Flag */}
        <div className="flex flex-col items-center space-y-2">
          <span
            className={`fi fi-${getCountryCodeForFlag(match.awayTeam.countryCode)} fis`}
            style={{ fontSize: '3.5rem' }}
          ></span>
          <span className={`text-lg font-bold ${getTextColorClass('text-neutral-DEFAULT')}`}>
            {isFinalized
              ? hasPrediction
                ? prediction.predictedAwayScore
                : '-'
              : awayScore !== ''
              ? awayScore
              : hasPrediction
              ? prediction.predictedAwayScore
              : '-'}
          </span>
        </div>
      </div>

      {/* Bottom Row: Status, Date, and Points/Submit Button */}
      <div className="flex items-center justify-between border-t border-neutral-DEFAULT/20 pt-2">
        <div className="flex items-center space-x-2">
          <svg
            className={`w-4 h-4 ${getTextColorClass('text-neutral-DEFAULT')}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <span className={`text-sm font-bold uppercase ${getTextColorClass('text-neutral-DEFAULT')}`}>
            {getMatchStatus()}
          </span>
          <span className={getTextColorClass('text-neutral-DEFAULT/60')}>|</span>
          <span className={`text-sm ${getTextColorClass('text-neutral-DEFAULT/70')}`}>
            {formatDate(match.scheduledAt)}
            {kickoffDisplay?.time ? ` · ${kickoffDisplay.time}` : ''}
          </span>
        </div>

        <div className="flex items-center">
          {isFinalized ? (
            // Show points for finalized matches
            <span className="text-xl font-bold">
              Total Points: <span style={{ color: cardStyle.color }}>{prediction?.points ?? 0}</span>
            </span>
          ) : (
            // Show submit button only when active (user has entered both predictions)
            canSubmit && (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="px-4 py-2 rounded-lg text-sm font-bold transition-colors bg-primary-medium text-white hover:bg-primary-dark"
              >
                {isSubmitting ? 'Sending...' : 'Send Guess'}
              </button>
            )
          )}
        </div>
      </div>
    </div>
  )
}
