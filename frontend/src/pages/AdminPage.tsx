import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { NavBar } from '@/components/layout/NavBar'
import { GroupComponent } from '@/components/standings/GroupComponent'
import { getStandings } from '@/services/standings'
import { getGames } from '@/services/matches'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { updateGameResult } from '@/services/admin'
import { Match } from '@/types/matches'

interface GroupMatches {
  groupLetter: string
  matches: Match[]
}

export const AdminPage: React.FC = () => {
  const [updatingGames, setUpdatingGames] = useState<Set<number>>(new Set())
  const [scoreInputs, setScoreInputs] = useState<Record<number, { home: string; away: string }>>({})

  // Fetch standings to get groups
  const { data: standingsData, isLoading: standingsLoading } = useQuery({
    queryKey: ['standings'],
    queryFn: getStandings,
  })

  // Fetch all games
  const { data: games, isLoading: gamesLoading, refetch: refetchGames } = useQuery({
    queryKey: ['adminGames'],
    queryFn: () => getGames(),
  })

  // Organize games by group
  const gamesByGroup = React.useMemo(() => {
    if (!games || !standingsData) return []

    const grouped: GroupMatches[] = []

    standingsData.groups.forEach((group) => {
      const groupGames = games.filter((game) => {
        // Match group letter directly (group.letter is already extracted from "Group A" -> "A")
        if (!game.group?.letter) return false
        return game.group.letter.trim().toUpperCase() === group.groupLetter.trim().toUpperCase()
      })
      if (groupGames.length > 0) {
        grouped.push({
          groupLetter: group.groupLetter,
          matches: groupGames.sort((a, b) => {
            // Sort by match date, then by scheduled time
            const dateA = a.matchDate || a.scheduledAt
            const dateB = b.matchDate || b.scheduledAt
            return new Date(dateA).getTime() - new Date(dateB).getTime()
          }),
        })
      }
    })

    return grouped
  }, [games, standingsData])

  // Initialize score inputs from existing game data
  React.useEffect(() => {
    if (games) {
      const inputs: Record<number, { home: string; away: string }> = {}
      games.forEach((game) => {
        inputs[game.id] = {
          home: game.homeScore?.toString() || '',
          away: game.awayScore?.toString() || '',
        }
      })
      setScoreInputs(inputs)
    }
  }, [games])

  const handleScoreChange = (gameId: number, team: 'home' | 'away', value: string) => {
    setScoreInputs((prev) => ({
      ...prev,
      [gameId]: {
        ...prev[gameId],
        [team]: value,
      },
    }))
  }

  const handleUpdateGame = async (game: Match) => {
    const inputs = scoreInputs[game.id]
    if (!inputs) return

    const homeScore = parseInt(inputs.home, 10)
    const awayScore = parseInt(inputs.away, 10)

    if (isNaN(homeScore) || isNaN(awayScore)) {
      alert('Please enter valid scores for both teams')
      return
    }

    setUpdatingGames((prev) => new Set(prev).add(game.id))

    try {
      await updateGameResult(game.id, homeScore, awayScore)
      // Refetch games to get updated data
      await refetchGames()
      alert('Game result updated successfully!')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update game result')
    } finally {
      setUpdatingGames((prev) => {
        const newSet = new Set(prev)
        newSet.delete(game.id)
        return newSet
      })
    }
  }

  if (standingsLoading || gamesLoading) {
    return (
      <div className="min-h-screen bg-neutral-light">
        <NavBar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-neutral-DEFAULT">Admin Panel</h1>
          <p className="text-sm text-neutral-DEFAULT/70 mt-2">
            Update match results for the 2026 FIFA World Cup
          </p>
        </div>

        {gamesByGroup.length === 0 && !standingsLoading && !gamesLoading && (
          <div className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            <p className="text-neutral-DEFAULT/70">
              {games && games.length > 0
                ? 'No group stage matches found. All matches may be knockout rounds.'
                : 'No matches found.'}
            </p>
            {games && games.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-neutral-DEFAULT/70">
                  Total games loaded: {games.length}
                </p>
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm text-primary-medium">
                    Debug: Show game details
                  </summary>
                  <pre className="mt-2 text-xs bg-neutral-light p-2 rounded overflow-auto max-h-96">
                    {JSON.stringify(
                      games.map((g) => ({
                        id: g.id,
                        homeTeam: g.homeTeam.name,
                        awayTeam: g.awayTeam.name,
                        group: g.group,
                      })),
                      null,
                      2
                    )}
                  </pre>
                </details>
              </div>
            )}
          </div>
        )}

        {gamesByGroup.map((groupData) => {
          const groupStanding = standingsData?.groups.find(
            (g) => g.groupLetter.toUpperCase() === groupData.groupLetter.toUpperCase()
          )

          return (
            <div key={groupData.groupLetter} className="mb-8">
              {/* Group Standings Table */}
              {groupStanding && (
                <div className="mb-4">
                  <GroupComponent group={groupStanding} />
                </div>
              )}

              {/* Matches List */}
              <div className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
                <h3 className="text-lg font-bold text-neutral-DEFAULT mb-4">
                  Group {groupData.groupLetter} Matches ({groupData.matches.length})
                </h3>
                <div className="space-y-4">
                  {groupData.matches.map((match) => {
                    const inputs = scoreInputs[match.id] || { home: '', away: '' }
                    const isUpdating = updatingGames.has(match.id)

                    return (
                      <div
                        key={match.id}
                        className="flex items-center justify-between p-4 border border-neutral-DEFAULT/20 rounded-lg hover:bg-neutral-light/50 transition-colors"
                      >
                        {/* Home Team */}
                        <div className="flex items-center space-x-3 flex-1">
                          <span
                            className={`fi fi-${getCountryCodeForFlag(match.homeTeam.countryCode)} fis`}
                            style={{ fontSize: '1.5rem' }}
                          ></span>
                          <span className="font-medium text-neutral-DEFAULT min-w-[120px]">
                            {match.homeTeam.name}
                          </span>
                        </div>

                        {/* Score Inputs */}
                        <div className="flex items-center space-x-2 mx-4">
                          <input
                            type="number"
                            min="0"
                            value={inputs.home}
                            onChange={(e) => handleScoreChange(match.id, 'home', e.target.value)}
                            disabled={isUpdating}
                            className="w-16 px-2 py-1 border border-neutral-DEFAULT/20 rounded text-center text-neutral-DEFAULT focus:outline-none focus:ring-2 focus:ring-primary-medium disabled:opacity-50"
                            placeholder="0"
                          />
                          <span className="text-neutral-DEFAULT font-bold">X</span>
                          <input
                            type="number"
                            min="0"
                            value={inputs.away}
                            onChange={(e) => handleScoreChange(match.id, 'away', e.target.value)}
                            disabled={isUpdating}
                            className="w-16 px-2 py-1 border border-neutral-DEFAULT/20 rounded text-center text-neutral-DEFAULT focus:outline-none focus:ring-2 focus:ring-primary-medium disabled:opacity-50"
                            placeholder="0"
                          />
                        </div>

                        {/* Away Team */}
                        <div className="flex items-center space-x-3 flex-1 justify-end">
                          <span className="font-medium text-neutral-DEFAULT min-w-[120px] text-right">
                            {match.awayTeam.name}
                          </span>
                          <span
                            className={`fi fi-${getCountryCodeForFlag(match.awayTeam.countryCode)} fis`}
                            style={{ fontSize: '1.5rem' }}
                          ></span>
                        </div>

                        {/* Update Button */}
                        <div className="ml-4">
                          <button
                            onClick={() => handleUpdateGame(match)}
                            disabled={isUpdating || !inputs.home || !inputs.away}
                            className="px-4 py-2 bg-primary-medium text-white rounded-md hover:bg-primary-DEFAULT focus:outline-none focus:ring-2 focus:ring-primary-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            {isUpdating ? 'Updating...' : 'Update'}
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

