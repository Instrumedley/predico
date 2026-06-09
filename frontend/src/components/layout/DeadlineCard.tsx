import React, { useState, useEffect } from 'react'
import { getNextMatch } from '@/services/matches'
import { calculateDeadline, getMatchKickoffUTC } from '@/utils/timezone'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'

interface DeadlineCardProps {
  roundNumber?: number
  deadlineDate?: Date
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

  // Fetch next match and calculate deadline
  useEffect(() => {
    // If deadlineDate is provided, use it
    if (deadlineDate) {
      setTargetDate(deadlineDate)
      setIsLoading(false)
      return
    }

    // Fetch the next match from the API
    const fetchNextMatch = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const nextMatchData = await getNextMatch()
        
        if (nextMatchData.matches && nextMatchData.matches.length > 0) {
          const match = nextMatchData.matches[0]
          
          // Calculate deadline (1 hour before match start)
          const deadline = calculateDeadline(
            match.matchDate,
            match.matchTime,
            match.timezone
          )

          if (deadline) {
            setTargetDate(deadline)
            setMatchInfo({
              homeTeam: match.homeTeam.name,
              awayTeam: match.awayTeam.name,
              homeTeamCountryCode: match.homeTeam.countryCode,
              awayTeamCountryCode: match.awayTeam.countryCode,
              roundName: match.round?.name || 'Next Match',
            })
          } else {
            const kickoff = getMatchKickoffUTC(match)
            if (!kickoff) {
              setError('No upcoming matches found')
              setTargetDate(null)
              return
            }
            const fallbackDeadline = new Date(kickoff.getTime() - 60 * 60 * 1000)
            setTargetDate(fallbackDeadline)
            setMatchInfo({
              homeTeam: match.homeTeam.name,
              awayTeam: match.awayTeam.name,
              homeTeamCountryCode: match.homeTeam.countryCode,
              awayTeamCountryCode: match.awayTeam.countryCode,
              roundName: match.round?.name || 'Next Match',
            })
          }
        } else {
          // No upcoming matches
          setError('No upcoming matches found')
          setTargetDate(null)
        }
      } catch (err) {
        console.error('Error fetching next match:', err)
        setError('Failed to load next match')
        setTargetDate(null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchNextMatch()
  }, [deadlineDate])

  // Update countdown timer
  useEffect(() => {
    if (!targetDate) {
      return
    }

    const calculateTimeLeft = () => {
      const now = new Date().getTime()
      const target = targetDate.getTime()
      const difference = target - now

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((difference % (1000 * 60)) / 1000),
        })
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
      }
    }

    // Calculate immediately
    calculateTimeLeft()

    // Update every second
    const interval = setInterval(calculateTimeLeft, 1000)

    return () => clearInterval(interval)
  }, [targetDate])

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
            {/* Days */}
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.days)}</div>
              <div className="text-sm opacity-90">days</div>
            </div>

            {/* Hours */}
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.hours)}</div>
              <div className="text-sm opacity-90">hrs</div>
            </div>

            {/* Minutes */}
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[80px]">
              <div className="text-3xl font-bold">{formatTime(timeLeft.minutes)}</div>
              <div className="text-sm opacity-90">mins</div>
            </div>

            {/* Seconds */}
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


