/**
 * League API service.
 */
import apiClient from './api'

export interface LeagueSummary {
  id: string
  name: string
  description?: string | null
  is_private: boolean
  created_at: string
  member_count: number
  is_member: boolean
}

export interface LeagueMemberRanking {
  rank: number
  user_id: number
  username: string
  total_points: number
}

export interface LeagueDetail {
  id: string
  name: string
  description?: string | null
  is_private: boolean
  created_at: string
  created_by: number
  member_count: number
  is_member: boolean
  is_creator: boolean
  rankings: LeagueMemberRanking[]
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

export interface LeagueInviteResponse {
  sent: string[]
  failed: string[]
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

export async function getLeagueDetail(leagueId: string): Promise<LeagueDetail> {
  const response = await apiClient.get<LeagueDetail>(`/api/v1/leagues/${leagueId}`)
  return response.data
}

export async function createLeague(payload: CreateLeaguePayload): Promise<CreateLeagueResponse> {
  const response = await apiClient.post<CreateLeagueResponse>('/api/v1/leagues', payload)
  return response.data
}

export async function joinLeague(leagueId: string, inviteCode?: string): Promise<LeagueDetail> {
  const response = await apiClient.post<LeagueDetail>(`/api/v1/leagues/${leagueId}/join`, {
    invite_code: inviteCode || undefined,
  })
  return response.data
}

export async function inviteToLeague(leagueId: string, emails: string[]): Promise<LeagueInviteResponse> {
  const response = await apiClient.post<LeagueInviteResponse>(`/api/v1/leagues/${leagueId}/invitations`, {
    emails,
  })
  return response.data
}

export async function acceptLeagueInvite(token: string): Promise<LeagueDetail> {
  const response = await apiClient.post<LeagueDetail>('/api/v1/leagues/accept-invite', { token })
  return response.data
}

export function parseEmailInput(input: string): string[] {
  const parts = input
    .split(/[,;\n]+/)
    .map((part) => part.trim().toLowerCase())
    .filter(Boolean)

  return [...new Set(parts)]
}
