/**
 * League API service.
 */
import apiClient from './api'

export interface LeagueSummary {
  id: number
  name: string
  description?: string | null
  is_private: boolean
  created_at: string
  member_count: number
  is_member: boolean
}

export interface CreateLeaguePayload {
  name: string
  description?: string
  is_private: boolean
  password?: string
}

export interface CreateLeagueResponse extends LeagueSummary {
  invite_code?: string | null
}

export async function getMyLeagues(): Promise<LeagueSummary[]> {
  const response = await apiClient.get<LeagueSummary[]>('/api/v1/leagues/me')
  return response.data
}

export async function getAllLeagues(search?: string): Promise<LeagueSummary[]> {
  const response = await apiClient.get<LeagueSummary[]>('/api/v1/leagues', {
    params: search ? { search } : undefined,
  })
  return response.data
}

export async function createLeague(payload: CreateLeaguePayload): Promise<CreateLeagueResponse> {
  const response = await apiClient.post<CreateLeagueResponse>('/api/v1/leagues', payload)
  return response.data
}

export async function joinLeague(leagueId: number, inviteCode?: string): Promise<LeagueSummary> {
  const response = await apiClient.post<LeagueSummary>(
    `/api/v1/leagues/${leagueId}/join`,
    null,
    { params: inviteCode ? { invite_code: inviteCode } : undefined }
  )
  return response.data
}
