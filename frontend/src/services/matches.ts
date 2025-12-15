/**
 * Matches/Games API service
 */
import apiClient from './api'
import { Match, NextMatchData, LatestResultsData } from '@/types/matches'
import { AxiosError } from 'axios'

const API_PREFIX = '/api/v1'

/**
 * API response types
 */
interface ApiTeam {
  id: number
  name: string
  country_code: string
  flag_emoji?: string | null
}

interface ApiStadium {
  id: number
  name: string
  city: string
}

interface ApiRound {
  id: number
  name: string
  round_type: string
}

interface ApiGroup {
  id: number
  name: string
}

interface ApiMatchResponse {
  id: number
  home_team: ApiTeam
  away_team: ApiTeam
  scheduled_at: string
  match_date?: string | null
  status: 'scheduled' | 'live' | 'finished' | 'cancelled' | 'postponed'
  home_score?: number | null
  away_score?: number | null
  home_penalty_score?: number | null
  away_penalty_score?: number | null
  stadium?: ApiStadium | null
  round: ApiRound
  group?: ApiGroup | null
  match_number?: number | null
}

/**
 * Transform API response to frontend format
 */
function transformMatchResponse(match: ApiMatchResponse): Match {
  return {
    id: match.id,
    homeTeam: {
      id: match.home_team.id,
      name: match.home_team.name,
      countryCode: match.home_team.country_code,
      flagEmoji: match.home_team.flag_emoji ?? undefined,
    },
    awayTeam: {
      id: match.away_team.id,
      name: match.away_team.name,
      countryCode: match.away_team.country_code,
      flagEmoji: match.away_team.flag_emoji ?? undefined,
    },
    scheduledAt: match.scheduled_at,
    matchDate: match.match_date ?? undefined,
    status: match.status,
    homeScore: match.home_score ?? undefined,
    awayScore: match.away_score ?? undefined,
    homePenaltyScore: match.home_penalty_score ?? undefined,
    awayPenaltyScore: match.away_penalty_score ?? undefined,
    stadium: match.stadium
      ? {
          id: match.stadium.id,
          name: match.stadium.name,
          city: match.stadium.city,
        }
      : undefined,
    round: match.round
      ? {
          id: match.round.id,
          name: match.round.name,
          number: 0, // Not provided by API, can be calculated if needed
        }
      : undefined,
    group: match.group
      ? {
          id: match.group.id,
          letter: match.group.name.replace(/^Group\s+/i, '').trim(),
        }
      : undefined,
    matchNumber: match.match_number ?? undefined,
  }
}

/**
 * Get next scheduled match
 */
export async function getNextMatch(): Promise<NextMatchData> {
  try {
    const response = await apiClient.get<ApiMatchResponse>(`${API_PREFIX}/games/next`)
    return {
      matches: [transformMatchResponse(response.data)],
    }
  } catch (error) {
    const axiosError = error as AxiosError
    if (axiosError.response?.status === 404) {
      return { matches: [] }
    }
    throw error
  }
}

/**
 * Get latest finished matches
 */
export async function getLatestResults(): Promise<LatestResultsData> {
  const response = await apiClient.get<ApiMatchResponse[]>(`${API_PREFIX}/games/latest?limit=5`)
  return {
    matches: response.data.map(transformMatchResponse),
  }
}

/**
 * Query parameters for getGames function
 */
export interface GetGamesParams {
  status?: string
  roundId?: number
  groupId?: number
  limit?: number
  offset?: number
}

/**
 * Get all games with optional filters
 * 
 * @param params - Optional query parameters to filter games
 * @returns Array of matches
 * 
 * @example
 * ```ts
 * const games = await getGames({ status: 'scheduled', limit: 10 })
 * ```
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function getGames(params?: GetGamesParams): Promise<Match[]> {
  const queryParams: GetGamesParams | undefined = params
  const response = await apiClient.get<ApiMatchResponse[]>(`${API_PREFIX}/games`, { params: queryParams })
  return response.data.map(transformMatchResponse)
}

/**
 * Get a specific game by ID
 * 
 * @param gameId - The ID of the game to retrieve
 * @returns The match data
 * 
 * @example
 * ```ts
 * const game = await getGame(123)
 * ```
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function getGame(gameId: number): Promise<Match> {
  const response = await apiClient.get<ApiMatchResponse>(`${API_PREFIX}/games/${gameId}`)
  return transformMatchResponse(response.data)
}

