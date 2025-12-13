/**
 * Mock data for matches
 * TODO: Replace with real API data from backend
 */

import { Match, NextMatchData, LatestResultsData } from '@/types/matches'

// Helper to create a date in the future
const futureDate = (days: number, hours: number = 0): string => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(date.getHours() + hours)
  return date.toISOString()
}

// Helper to create a date in the past
const pastDate = (days: number, hours: number = 0): string => {
  const date = new Date()
  date.setDate(date.getDate() - days)
  date.setHours(date.getHours() - hours)
  return date.toISOString()
}

export const mockNextMatch: NextMatchData = {
  matches: [
    {
      id: 1,
      homeTeam: {
        id: 1,
        name: 'Argentina',
        countryCode: 'ARG',
      },
      awayTeam: {
        id: 2,
        name: 'Brazil',
        countryCode: 'BRA',
      },
      scheduledAt: futureDate(2, 20), // 2 days, 20 hours from now
      status: 'scheduled',
      stadium: {
        id: 1,
        name: 'Estadio Banorte',
        city: 'Mexico City',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 1,
        letter: 'A',
      },
      matchNumber: 1,
    },
  ],
}

// Example of round 3 with 2 simultaneous matches
export const mockNextMatchRound3: NextMatchData = {
  matches: [
    {
      id: 15,
      homeTeam: {
        id: 1,
        name: 'Argentina',
        countryCode: 'ARG',
      },
      awayTeam: {
        id: 3,
        name: 'Uruguay',
        countryCode: 'URU',
      },
      scheduledAt: futureDate(3, 18),
      status: 'scheduled',
      stadium: {
        id: 1,
        name: 'Estadio Banorte',
        city: 'Mexico City',
      },
      round: {
        id: 3,
        name: 'Group Stage',
        number: 3,
      },
      group: {
        id: 1,
        letter: 'A',
      },
      matchNumber: 15,
    },
    {
      id: 16,
      homeTeam: {
        id: 2,
        name: 'Brazil',
        countryCode: 'BRA',
      },
      awayTeam: {
        id: 4,
        name: 'Chile',
        countryCode: 'CHI',
      },
      scheduledAt: futureDate(3, 18), // Same time
      status: 'scheduled',
      stadium: {
        id: 2,
        name: 'MetLife Stadium',
        city: 'New York/New Jersey',
      },
      round: {
        id: 3,
        name: 'Group Stage',
        number: 3,
      },
      group: {
        id: 1,
        letter: 'A',
      },
      matchNumber: 16,
    },
  ],
}

export const mockLatestResults: LatestResultsData = {
  matches: [
    {
      id: 10,
      homeTeam: {
        id: 5,
        name: 'France',
        countryCode: 'FRA',
      },
      awayTeam: {
        id: 6,
        name: 'England',
        countryCode: 'ENG',
      },
      scheduledAt: pastDate(1, 2),
      status: 'finished',
      homeScore: 2,
      awayScore: 1,
      stadium: {
        id: 3,
        name: 'AT&T Stadium',
        city: 'Dallas',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 2,
        letter: 'B',
      },
      matchNumber: 10,
    },
    {
      id: 9,
      homeTeam: {
        id: 7,
        name: 'USA',
        countryCode: 'USA',
      },
      awayTeam: {
        id: 8,
        name: 'Mexico',
        countryCode: 'MEX',
      },
      scheduledAt: pastDate(1, 5),
      status: 'finished',
      homeScore: 1,
      awayScore: 1,
      stadium: {
        id: 4,
        name: 'GEHA Field at Arrowhead Stadium',
        city: 'Kansas City',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 3,
        letter: 'C',
      },
      matchNumber: 9,
    },
    {
      id: 8,
      homeTeam: {
        id: 9,
        name: 'Netherlands',
        countryCode: 'NED',
      },
      awayTeam: {
        id: 10,
        name: 'Belgium',
        countryCode: 'BEL',
      },
      scheduledAt: pastDate(2, 3),
      status: 'finished',
      homeScore: 3,
      awayScore: 0,
      stadium: {
        id: 5,
        name: 'NRG Stadium',
        city: 'Houston',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 4,
        letter: 'D',
      },
      matchNumber: 8,
    },
    {
      id: 7,
      homeTeam: {
        id: 11,
        name: 'Japan',
        countryCode: 'JPN',
      },
      awayTeam: {
        id: 12,
        name: 'S. Korea',
        countryCode: 'KOR',
      },
      scheduledAt: pastDate(2, 8),
      status: 'finished',
      homeScore: 2,
      awayScore: 2,
      stadium: {
        id: 6,
        name: 'Mercedes-Benz Stadium',
        city: 'Atlanta',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 5,
        letter: 'E',
      },
      matchNumber: 7,
    },
    {
      id: 6,
      homeTeam: {
        id: 13,
        name: 'Morocco',
        countryCode: 'MAR',
      },
      awayTeam: {
        id: 14,
        name: 'Senegal',
        countryCode: 'SEN',
      },
      scheduledAt: pastDate(3, 1),
      status: 'finished',
      homeScore: 1,
      awayScore: 0,
      stadium: {
        id: 7,
        name: 'SoFi Stadium',
        city: 'Los Angeles',
      },
      round: {
        id: 1,
        name: 'Group Stage',
        number: 1,
      },
      group: {
        id: 6,
        letter: 'F',
      },
      matchNumber: 6,
    },
  ],
}

