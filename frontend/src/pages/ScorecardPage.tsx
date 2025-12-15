import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { NavBar } from '@/components/layout'
import { PredictionRowCard } from '@/components/predictions'
import { getGames } from '@/services/matches'
import { getUserPredictions, createOrUpdatePrediction, createOrUpdatePredictionsBatch } from '@/services/predictions'
import { Match } from '@/types/matches'
import { Prediction } from '@/services/predictions'
import { useFeedback } from '@/contexts/FeedbackContext'

interface GameWithPrediction extends Match {
  prediction?: Prediction | null
}

interface RoundSection {
  roundId: number
  roundName: string
  games: GameWithPrediction[]
}

export const ScorecardPage: React.FC = () => {
  const [collapsedRounds, setCollapsedRounds] = useState<Set<number>>(new Set())
  const [pendingPredictions, setPendingPredictions] = useState<Map<number, { homeScore: number; awayScore: number }>>(
    new Map()
  )

  const queryClient = useQueryClient()
  const { showFeedback } = useFeedback()

  // Fetch all games
  const { data: games = [], isLoading: gamesLoading } = useQuery<Match[]>({
    queryKey: ['games'],
    queryFn: () => getGames(),
    staleTime: 1 * 60 * 1000, // 1 minute
  })

  // Fetch user predictions
  const { data: predictions = [], isLoading: predictionsLoading } = useQuery<Prediction[]>({
    queryKey: ['userPredictions'],
    queryFn: getUserPredictions,
    staleTime: 30 * 1000, // 30 seconds
  })

  // Create a map of gameId -> prediction for quick lookup
  const predictionsMap = useMemo(() => {
    const map = new Map<number, Prediction>()
    predictions.forEach((pred) => {
      map.set(pred.gameId, pred)
    })
    return map
  }, [predictions])

  // Group games by round and merge with predictions
  const roundsData = useMemo(() => {
    const roundsMap = new Map<number, RoundSection>()

    games.forEach((game) => {
      const roundId = game.round?.id || 0
      const roundName = game.round?.name || 'Unknown Round'

      if (!roundsMap.has(roundId)) {
        roundsMap.set(roundId, {
          roundId,
          roundName,
          games: [],
        })
      }

      const round = roundsMap.get(roundId)!
      round.games.push({
        ...game,
        prediction: predictionsMap.get(game.id),
      })
    })

    // Sort games within each round by scheduled_at
    roundsMap.forEach((round) => {
      round.games.sort((a, b) => {
        const dateA = new Date(a.scheduledAt).getTime()
        const dateB = new Date(b.scheduledAt).getTime()
        return dateA - dateB
      })
    })

    // Convert to array and sort by round ID
    return Array.from(roundsMap.values()).sort((a, b) => a.roundId - b.roundId)
  }, [games, predictionsMap])

  // Mutation for submitting a single prediction
  const submitPredictionMutation = useMutation({
    mutationFn: ({ gameId, homeScore, awayScore }: { gameId: number; homeScore: number; awayScore: number }) =>
      createOrUpdatePrediction(gameId, homeScore, awayScore),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userPredictions'] })
      queryClient.invalidateQueries({ queryKey: ['games'] })
      showFeedback('Guess sent!', 'success')
    },
    onError: () => {
      showFeedback('There was an error sending your guess', 'error')
    },
  })

  // Mutation for batch submitting predictions
  const batchSubmitMutation = useMutation({
    mutationFn: (predictions: Array<{ game_id: number; predicted_home_score: number; predicted_away_score: number }>) =>
      createOrUpdatePredictionsBatch(predictions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userPredictions'] })
      queryClient.invalidateQueries({ queryKey: ['games'] })
      setPendingPredictions(new Map())
      showFeedback('All predictions have been correctly sent', 'success')
    },
    onError: () => {
      showFeedback('There was an error sending your predictions', 'error')
    },
  })

  const toggleRound = (roundId: number) => {
    setCollapsedRounds((prev) => {
      const next = new Set(prev)
      if (next.has(roundId)) {
        next.delete(roundId)
      } else {
        next.add(roundId)
      }
      return next
    })
  }

  const handlePredictionSubmit = (gameId: number, homeScore: number, awayScore: number) => {
    submitPredictionMutation.mutate({ gameId, homeScore, awayScore })
    // Remove from pending predictions if it was there
    setPendingPredictions((prev) => {
      const next = new Map(prev)
      next.delete(gameId)
      return next
    })
  }

  const handlePredictionChange = (gameId: number, homeScore: number, awayScore: number) => {
    setPendingPredictions((prev) => {
      const next = new Map(prev)
      next.set(gameId, { homeScore, awayScore })
      return next
    })
  }

  const handleSaveAllPredictions = () => {
    const predictionsToSubmit = Array.from(pendingPredictions.entries()).map(([gameId, scores]) => ({
      game_id: gameId,
      predicted_home_score: scores.homeScore,
      predicted_away_score: scores.awayScore,
    }))

    if (predictionsToSubmit.length > 0) {
      batchSubmitMutation.mutate(predictionsToSubmit)
    }
  }

  const isLoading = gamesLoading || predictionsLoading

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 className="text-3xl font-bold text-neutral-DEFAULT mb-6">Scorecard</h1>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-neutral-DEFAULT/70">Loading predictions...</p>
          </div>
        ) : roundsData.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-neutral-DEFAULT/70">No games available</p>
          </div>
        ) : (
          <>
            {roundsData.map((round) => {
              const isCollapsed = collapsedRounds.has(round.roundId)

              return (
                <div key={round.roundId} className="mb-6">
                  {/* Round Header */}
                  <button
                    onClick={() => toggleRound(round.roundId)}
                    className="w-full flex items-center justify-between p-4 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm hover:bg-neutral-light transition-colors"
                  >
                    <h2 className="text-xl font-bold text-neutral-DEFAULT">{round.roundName}</h2>
                    <svg
                      className={`w-5 h-5 text-neutral-DEFAULT transition-transform ${
                        isCollapsed ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </button>

                  {/* Games List */}
                  {!isCollapsed && (
                    <div className="mt-4 space-y-4">
                      {round.games.map((game) => (
                        <PredictionRowCard
                          key={game.id}
                          match={game}
                          prediction={game.prediction}
                          onPredictionSubmit={handlePredictionSubmit}
                          onPredictionChange={handlePredictionChange}
                          isSubmitting={submitPredictionMutation.isPending}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )
            })}

            {/* Save All Predictions Button */}
            {pendingPredictions.size > 0 && (
              <div className="mt-8 flex justify-center">
                <button
                  onClick={handleSaveAllPredictions}
                  disabled={batchSubmitMutation.isPending}
                  className={`px-6 py-3 rounded-lg font-bold transition-colors ${
                    batchSubmitMutation.isPending
                      ? 'bg-neutral-DEFAULT/20 text-neutral-DEFAULT/50 cursor-not-allowed'
                      : 'bg-primary-medium text-white hover:bg-primary-dark'
                  }`}
                >
                  {batchSubmitMutation.isPending ? 'Saving...' : 'Save All Predictions'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
