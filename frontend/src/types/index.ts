/**
 * TypeScript type definitions.
 */

export interface User {
  id: string
  email: string
  username: string
  created_at: string
}

export interface Game {
  id: string
  home_team: string
  away_team: string
  scheduled_at: string
  status: 'scheduled' | 'live' | 'finished'
  home_score?: number
  away_score?: number
}

export interface Prediction {
  id: string
  user_id: string
  game_id: string
  home_score: number
  away_score: number
  points?: number
  created_at: string
}

export interface League {
  id: string
  name: string
  description?: string | null
  is_private: boolean
  created_at: string
  member_count: number
  is_member?: boolean
}

export interface LeagueMember {
  id: string
  league_id: string
  user_id: string
  joined_at: string
  total_points: number
}

