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

