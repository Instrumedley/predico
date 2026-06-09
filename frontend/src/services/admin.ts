/**
 * Admin API service for managing games and match results.
 */
import apiClient from './api'

const API_PREFIX = '/api/v1'

export interface UpdateGameResultRequest {
  home_score: number
  away_score: number
}

export interface UpdateGameResultResponse {
  message: string
  game_id: number
  home_score: number
  away_score: number
  status: string
}

export interface ResetGameResponse {
  message: string
  game_id: number
  status: string
  predictions_reset: number
}

/**
 * Update game result (scores) and mark game as finished.
 * Only accessible by admin users.
 */
export async function updateGameResult(
  gameId: number,
  homeScore: number,
  awayScore: number
): Promise<UpdateGameResultResponse> {
  const response = await apiClient.put<UpdateGameResultResponse>(
    `${API_PREFIX}/admin/games/${gameId}/result`,
    {
      home_score: homeScore,
      away_score: awayScore,
    }
  )
  return response.data
}

/**
 * Reset a game to its original state (no result, status = scheduled).
 * This will reset the game status, clear scores, and reset all predictions.
 * Only accessible by admin users.
 */
export async function resetGame(gameId: number): Promise<ResetGameResponse> {
  const response = await apiClient.post<ResetGameResponse>(
    `${API_PREFIX}/admin/games/${gameId}/reset`
  )
  return response.data
}

export interface ResetAllGamesResponse {
  message: string
  games_reset: number
  predictions_reset: number
}

/**
 * Reset all games to their original state (no results, status = scheduled).
 * This will reset all game statuses, clear all scores, and reset all predictions.
 * This brings the system back to the initial state.
 * Only accessible by admin users.
 */
export async function resetAllGames(): Promise<ResetAllGamesResponse> {
  const response = await apiClient.post<ResetAllGamesResponse>(
    `${API_PREFIX}/admin/games/reset-all`
  )
  return response.data
}

export interface AdminUserSummary {
  id: number
  username: string
  email: string
  created_at: string
  total_predictions: number
  total_points: number
}

export interface AdminUserListResponse {
  users: AdminUserSummary[]
  total: number
}

export type AdminUserSort = 'username' | 'created_at'

export async function listAdminUsers(
  q?: string,
  sort: AdminUserSort = 'username'
): Promise<AdminUserListResponse> {
  const params = new URLSearchParams()
  if (q?.trim()) {
    params.set('q', q.trim())
  }
  params.set('sort', sort)
  const response = await apiClient.get<AdminUserListResponse>(
    `${API_PREFIX}/admin/users?${params.toString()}`
  )
  return response.data
}

export interface AdminUserPrediction {
  id: number
  predicted_home_score: number
  predicted_away_score: number
  points: number
  is_calculated: boolean
  game: {
    id: number
    status: string
    home_team: { id: number; name: string; country_code: string }
    away_team: { id: number; name: string; country_code: string }
    match_date?: string | null
    scheduled_at: string
  }
}

export interface AdminUserPredictionsResponse {
  user: AdminUserSummary
  predictions: AdminUserPrediction[]
  total_points: number
}

export async function getAdminUserPredictions(
  userId: number
): Promise<AdminUserPredictionsResponse> {
  const response = await apiClient.get<AdminUserPredictionsResponse>(
    `${API_PREFIX}/admin/users/${userId}/predictions`
  )
  return response.data
}

