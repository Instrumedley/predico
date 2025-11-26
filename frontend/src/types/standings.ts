/**
 * Types for World Cup group standings
 * These types will be used when we integrate with the backend
 */

export interface TeamStanding {
  position: number
  countryCode: string // ISO 3166-1 alpha-3 code (e.g., 'USA', 'BRA', 'ARG')
  countryName: string
  played: number
  wins: number
  draws: number
  losses: number
  goalsFor: number
  goalsAgainst: number
  goalDifference: number
  points: number
}

export interface GroupStanding {
  groupLetter: string // 'A' through 'L'
  teams: TeamStanding[]
}

export interface StandingsData {
  groups: GroupStanding[]
  lastUpdated?: string
}

