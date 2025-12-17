/**
 * Types for match/game data
 * These types will be used when we integrate with the backend
 */

export interface Team {
  id: number
  name: string
  countryCode: string
  flagEmoji?: string
}

export interface Match {
  id: number
  homeTeam: Team
  awayTeam: Team
  scheduledAt: string // ISO datetime string
  matchDate?: string // ISO date string
  matchTime?: string // Time string (HH:MM:SS)
  timezone?: string // Timezone string (e.g., "UTC-5")
  status: 'scheduled' | 'live' | 'finished' | 'cancelled' | 'postponed'
  homeScore?: number
  awayScore?: number
  homePenaltyScore?: number
  awayPenaltyScore?: number
  stadium?: {
    id: number
    name: string
    city: string
  }
  round?: {
    id: number
    name: string
    number: number
  }
  group?: {
    id: number
    letter: string
  }
  matchNumber?: number
}

export interface NextMatchData {
  matches: Match[] // 1 match usually, 2 matches during round 3 of group stage
}

export interface LatestResultsData {
  matches: Match[] // Max 5 finished matches
}

