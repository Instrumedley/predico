import apiClient from './api'
import {
  BracketMatch,
  BracketSideData,
  BracketSlot,
  BracketTeam,
  KnockoutBracketData,
  UpdateKnockoutMatchPayload,
} from '@/types/knockout'

const API_PREFIX = '/api/v1'

interface ApiBracketTeam {
  team_id: number
  country_code: string
  country_name: string
  flag_emoji?: string | null
}

interface ApiBracketSlot {
  label?: string
  team?: ApiBracketTeam
}

interface ApiBracketMatch {
  match_number: number
  home: ApiBracketSlot
  away: ApiBracketSlot
  home_score?: number | null
  away_score?: number | null
  winner_team_id?: number | null
  is_finished: boolean
}

interface ApiBracketSide {
  round_of32: ApiBracketMatch[]
  round_of16: ApiBracketMatch[]
  quarter_finals: ApiBracketMatch[]
  semi_final: ApiBracketMatch
}

interface ApiKnockoutBracket {
  left: ApiBracketSide
  right: ApiBracketSide
  final: ApiBracketMatch
  third_place: ApiBracketMatch
  third_place_combination_key?: string | null
}

function transformTeam(team: ApiBracketTeam): BracketTeam {
  return {
    teamId: team.team_id,
    countryCode: team.country_code,
    countryName: team.country_name,
    flagEmoji: team.flag_emoji,
  }
}

function transformSlot(slot: ApiBracketSlot): BracketSlot {
  return {
    label: slot.label,
    team: slot.team ? transformTeam(slot.team) : undefined,
  }
}

function transformMatch(match: ApiBracketMatch): BracketMatch {
  return {
    matchNumber: match.match_number,
    home: transformSlot(match.home),
    away: transformSlot(match.away),
    homeScore: match.home_score,
    awayScore: match.away_score,
    winnerTeamId: match.winner_team_id,
    isFinished: match.is_finished,
  }
}

function transformSide(side: ApiBracketSide): BracketSideData {
  return {
    roundOf32: side.round_of32.map(transformMatch),
    roundOf16: side.round_of16.map(transformMatch),
    quarterFinals: side.quarter_finals.map(transformMatch),
    semiFinal: transformMatch(side.semi_final),
  }
}

function transformBracket(data: ApiKnockoutBracket): KnockoutBracketData {
  return {
    left: transformSide(data.left),
    right: transformSide(data.right),
    final: transformMatch(data.final),
    thirdPlace: transformMatch(data.third_place),
    thirdPlaceCombinationKey: data.third_place_combination_key,
  }
}

export async function getKnockoutBracket(): Promise<KnockoutBracketData> {
  const response = await apiClient.get<ApiKnockoutBracket>(`${API_PREFIX}/knockout/bracket`)
  return transformBracket(response.data)
}

export async function getAdminKnockoutBracket(): Promise<KnockoutBracketData> {
  const response = await apiClient.get<ApiKnockoutBracket>(`${API_PREFIX}/admin/knockout/bracket`)
  return transformBracket(response.data)
}

export async function updateKnockoutMatchResult(
  matchNumber: number,
  payload: UpdateKnockoutMatchPayload
): Promise<KnockoutBracketData> {
  const response = await apiClient.put<{ bracket: ApiKnockoutBracket }>(
    `${API_PREFIX}/admin/knockout/matches/${matchNumber}`,
    {
      home_score: payload.homeScore,
      away_score: payload.awayScore,
      winner_team_id: payload.winnerTeamId,
    }
  )
  return transformBracket(response.data.bracket)
}

export async function resetKnockoutMatchResult(matchNumber: number): Promise<void> {
  await apiClient.delete(`${API_PREFIX}/admin/knockout/matches/${matchNumber}`)
}
