import React, { useState, useEffect, useCallback, useRef } from 'react'
import { getNextDeadlineMatch } from '@/services/matches'
import { Match } from '@/types/matches'
import { calculateDeadline, getMatchKickoffUTC } from '@/utils/timezone'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'

interface DeadlineCardProps {
  roundNumber?: number
  deadlineDate?: Date
}

function matchToDeadlineTarget(match: Match): Date | null {
  const deadline = calculateDeadline(match.matchDate, match.matchTime, match.timezone)
  if (deadline) {
    return deadline
  }

  const kickoff = getMatchKickoffUTC(match)
  if (!kickoff) {
    return null
  }

  return new Date(kickoff.getTime() - 60 * 60 * 1000)
}

function matchToInfo(match: Match) {
  return {
    homeTeam: match.homeTeam?.name ?? match.homeSlotLabel ?? 'TBD',
    awayTeam: match.awayTeam?.name ?? match.awaySlotLabel ?? 'TBD',
    homeTeamCountryCode: match.homeTeam?.countryCode ?? '',
    awayTeamCountryCode: match.awayTeam?.countryCode ?? '',
    roundName: match.round?.name || 'Next Match',
  }
}

export const DeadlineCard: React.FC<DeadlineCardProps> = ({
  roundNumber,
  deadlineDate,
}) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })
  const [matchInfo, setMatchInfo] = useState<{
    homeTeam: string
    awayTeam: string
    homeTeamCountryCode: string
    awayTeamCountryCode: string
    roundName: string
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [targetDate, setTargetDate] = useState<Date | null>(null)
  const expiredTargetRef = useRef<number | null>(null)

  const fetchNextDeadline = useCallback(async (options?: { silent?: boolean }) => {
    if (deadlineDate) {
      setTargetDate(deadlineDate)
      setIsLoading(false)
      return
    }

    try {
      if (!options?.silent) {
        setIsLoading(true)
      }
      setError(null)
      const match = await getNextDeadlineMatch()

      if (!match) {
        setError('No upcoming prediction deadlines')
        setTargetDate(null)
        setMatchInfo(null)
        return
      }

      const deadline = matchToDeadlineTarget(match)
      if (!deadline) {
        setError('No upcoming prediction deadlines')
        setTargetDate(null)
        setMatchInfo(null)
        return
      }

      setTargetDate(deadline)
      setMatchInfo(matchToInfo(match))
      expiredTargetRef.current = null
    } catch (err) {
      console.error('Error fetching next deadline:', err)
      setError('Failed to load next deadline')
      setTargetDate(null)
      setMatchInfo(null)
    } finally {
      if (!options?.silent) {
        setIsLoading(false)
      }
    }
  }, [deadlineDate])

  useEffect(() => {
    fetchNextDeadline()
  }, [fetchNextDeadline])

  useEffect(() => {
    if (!targetDate) {
      return
    }

    const calculateTimeLeft = () => {
      const now = Date.now()
      const target = targetDate.getTime()
      const difference = target - now

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((difference % (1000 * 60)) / 1000),
        })
        return
      }

      setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })

      if (!deadlineDate && expiredTargetRef.current !== target) {
        expiredTargetRef.current = target
        fetchNextDeadline({ silent: true })
      }
    }

    calculateTimeLeft()
    const interval = setInterval(calculateTimeLeft, 1000)
    return () => clearInterval(interval)
  }, [targetDate, deadlineDate, fetchNextDeadline])

  const formatTime = (value: number): string => {
    return value.toString().padStart(2, '0')
  }

  const displayRoundName = matchInfo?.roundName || (roundNumber ? `ROUND ${roundNumber}` : 'NEXT MATCH')

  if (isLoading) {
    return (
      <div className="flex justify-center py-6">
        <div className="rounded-xl shadow-lg p-8 text-center min-w-[400px]" style={{ backgroundColor: 'rgba(245, 166, 17, 0.85)' }}>
          <div className="text-white">
            <h2 className="text-2xl font-bold mb-6">Loading next deadline...</h2>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center py-6">
        <div className="rounded-xl shadow-lg p-8 text-center min-w-[400px]" style={{ backgroundColor: 'rgba(245, 166, 17, 0.85)' }}>
          <div className="text-white">
            <h2 className="text-2xl font-bold mb-6">NEXT DEADLINE</h2>
            <p className="text-lg opacity-90">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-center py-6">
      <div className="rounded-xl shadow-lg p-8 text-center min-w-[400px]" style={{ backgroundColor: 'rgba(245, 166, 17, 0.85)' }}>
        <div className="text-white">
          <h2 className="text-2xl font-bold mb-2">NEXT DEADLINE: {displayRoundName}</h2>
          {matchInfo && (
            <div className="flex items-center justify-center gap-2 text-lg mb-4 opacity-90">
              <span>{abbreviateCountryName(matchInfo.homeTeam)}</span>
              <span
                className={`fi fi-${getCountryCodeForFlag(matchInfo.homeTeamCountryCode)} fis`}
                style={{ fontSize: '1.25rem' }}
              ></span>
              <span className="mx-1">vs</span>
              <span
                className={`fi fi-${getCountryCodeForFlag(matchInfo.awayTeamCountryCode)} fis`}
                style={{ fontSize: '1.25rem' }}
              ></span>
              <span>{abbreviateCountryName(matchInfo.awayTeam)}</span>
            </div>
          )}

          <div className="flex justify-center items-center space-x-4">
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.days)}</div>
              <div className="text-sm opacity-90">days</div>
            </div>

            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.hours)}</div>
              <div className="text-sm opacity-90">hrs</div>
            </div>

            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.minutes)}</div>
              <div className="text-sm opacity-90">mins</div>
            </div>

            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.seconds)}</div>
              <div className="text-sm opacity-90">secs</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
