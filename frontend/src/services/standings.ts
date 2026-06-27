/**
 * Standings API service
 */
import apiClient from './api'
import { StandingsData } from '@/types/standings'

const API_PREFIX = '/api/v1'

/**
 * Transform API response to frontend format
 */
function transformStandingsResponse(data: any): StandingsData {
  return {
    groups: data.groups.map((group: any) => ({
      groupLetter: group.group_letter,
      isComplete: group.is_complete ?? false,
      teams: group.teams.map((team: any) => ({
        position: team.position,
        countryCode: team.country_code,
        countryName: team.country_name,
        flagEmoji: team.flag_emoji,
        played: team.played,
        wins: team.wins,
        draws: team.draws,
        losses: team.losses,
        goalsFor: team.goals_for,
        goalsAgainst: team.goals_against,
        goalDifference: team.goal_difference,
        points: team.points,
        qualifiedToKnockout: team.qualified_to_knockout ?? false,
      })),
    })),
  }
}

/**
 * Get all group stage standings
 */
export async function getStandings(): Promise<StandingsData> {
  const response = await apiClient.get(`${API_PREFIX}/standings`)
  return transformStandingsResponse(response.data)
}

/**
 * Get standings for a specific group
 */
export async function getGroupStandings(groupLetter: string): Promise<StandingsData['groups'][0]> {
  const response = await apiClient.get(`${API_PREFIX}/standings/${groupLetter}`)
  const group = response.data
  return {
    groupLetter: group.group_letter,
    isComplete: group.is_complete ?? false,
    teams: group.teams.map((team: any) => ({
      position: team.position,
      countryCode: team.country_code,
      countryName: team.country_name,
      flagEmoji: team.flag_emoji,
      played: team.played,
      wins: team.wins,
      draws: team.draws,
      losses: team.losses,
      goalsFor: team.goals_for,
      goalsAgainst: team.goals_against,
      goalDifference: team.goal_difference,
      points: team.points,
      qualifiedToKnockout: team.qualified_to_knockout ?? false,
    })),
  }
}

