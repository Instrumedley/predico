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

