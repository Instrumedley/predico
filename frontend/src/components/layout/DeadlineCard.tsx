import React, { useState, useEffect } from 'react'

interface DeadlineCardProps {
  roundNumber?: number
  deadlineDate?: Date
}

export const DeadlineCard: React.FC<DeadlineCardProps> = ({
  roundNumber = 13,
  deadlineDate,
}) => {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    // If no deadlineDate provided, set a default (3 days from now)
    const targetDate = deadlineDate || new Date(Date.now() + 3 * 24 * 60 * 60 * 1000)

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
  }, [deadlineDate])

  const formatTime = (value: number): string => {
    return value.toString().padStart(2, '0')
  }

  return (
    <div className="flex justify-center py-6">
      <div className="bg-gradient-to-br from-primary-medium to-primary-DEFAULT rounded-xl shadow-lg p-8 text-center min-w-[400px]">
        <div className="text-white">
          <h2 className="text-2xl font-bold mb-6">NEXT DEADLINE: ROUND {roundNumber}</h2>
          
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


