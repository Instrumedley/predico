/**
 * Predictions API service
 */
import apiClient from './api'
import { AxiosError } from 'axios'

const API_PREFIX = '/api/v1'

/**
 * API response types
 */
interface ApiPredictionResponse {
  id: number
  user_id: number
  game_id: number
  predicted_home_score: number
  predicted_away_score: number
  points?: number | null
  created_at: string
  updated_at: string
}

export interface Prediction {
  id: number
  userId: number
  gameId: number
  predictedHomeScore: number
  predictedAwayScore: number
  points?: number
  createdAt: string
  updatedAt: string
}

export interface CreatePredictionRequest {
  game_id: number
  predicted_home_score: number
  predicted_away_score: number
}

export interface CreatePredictionResponse {
  id: number
  user_id: number
  game_id: number
  predicted_home_score: number
  predicted_away_score: number
  points: number
  created_at: string
  updated_at: string
}

export interface BatchCreatePredictionRequest {
  predictions: CreatePredictionRequest[]
}

/**
 * Transform API response to frontend format
 */
function transformPredictionResponse(prediction: ApiPredictionResponse): Prediction {
  return {
    id: prediction.id,
    userId: prediction.user_id,
    gameId: prediction.game_id,
    predictedHomeScore: prediction.predicted_home_score,
    predictedAwayScore: prediction.predicted_away_score,
    points: prediction.points ?? undefined,
    createdAt: prediction.created_at,
    updatedAt: prediction.updated_at,
  }
}

/**
 * Get all predictions for the current user
 */
export async function getUserPredictions(): Promise<Prediction[]> {
  try {
    const response = await apiClient.get<ApiPredictionResponse[]>(`${API_PREFIX}/predictions`)
    return response.data.map(transformPredictionResponse)
  } catch (error) {
    const axiosError = error as AxiosError
    if (axiosError.response?.status === 404) {
      return []
    }
    throw error
  }
}

/**
 * Get prediction for a specific game
 */
export async function getPredictionForGame(gameId: number): Promise<Prediction | null> {
  try {
    const response = await apiClient.get<ApiPredictionResponse>(`${API_PREFIX}/predictions/game/${gameId}`)
    return transformPredictionResponse(response.data)
  } catch (error) {
    const axiosError = error as AxiosError
    if (axiosError.response?.status === 404) {
      return null
    }
    throw error
  }
}

/**
 * Create or update a prediction for a game
 */
export async function createOrUpdatePrediction(
  gameId: number,
  predictedHomeScore: number,
  predictedAwayScore: number
): Promise<Prediction> {
  const response = await apiClient.post<CreatePredictionResponse>(`${API_PREFIX}/predictions`, {
    game_id: gameId,
    predicted_home_score: predictedHomeScore,
    predicted_away_score: predictedAwayScore,
  })
  return transformPredictionResponse(response.data)
}

/**
 * Create or update multiple predictions in batch
 */
export async function createOrUpdatePredictionsBatch(
  predictions: CreatePredictionRequest[]
): Promise<Prediction[]> {
  const response = await apiClient.post<ApiPredictionResponse[]>(
    `${API_PREFIX}/predictions/batch`,
    { predictions }
  )
  return response.data.map(transformPredictionResponse)
}
