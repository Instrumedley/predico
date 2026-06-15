/**
 * Public config / feature flags from the API.
 */
import apiClient from './api'

export interface FeatureFlags {
  league_progress_chart: boolean
  knockout_stage: boolean
  knockout_stage_default: boolean
}

export async function getFeatureFlags(): Promise<FeatureFlags> {
  const response = await apiClient.get<FeatureFlags>('/api/v1/config/features')
  return response.data
}
