import React, { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { NavBar } from '@/components/layout'
import { JoinLeagueModal } from '@/components/leagues'
import { getAllLeagues, joinLeague, LeagueSummary } from '@/services/leagues'
import { useFeedback } from '@/contexts/FeedbackContext'
import { format } from 'date-fns'

export const GlobalLeaguesPage: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showFeedback } = useFeedback()
  const [searchInput, setSearchInput] = useState('')
  const [joinTarget, setJoinTarget] = useState<LeagueSummary | null>(null)
  const [joinError, setJoinError] = useState('')

  const { data: leagues = [], isLoading, error } = useQuery({
    queryKey: ['allLeagues'],
    queryFn: () => getAllLeagues(),
    staleTime: 30 * 1000,
  })

  const joinMutation = useMutation({
    mutationFn: ({ leagueId, password }: { leagueId: string; password?: string }) =>
      joinLeague(leagueId, password),
    onSuccess: (data) => {
      setJoinTarget(null)
      setJoinError('')
      queryClient.invalidateQueries({ queryKey: ['allLeagues'] })
      queryClient.invalidateQueries({ queryKey: ['myLeagues'] })
      showFeedback(`You joined ${data.name}.`, 'success')
      navigate(`/leagues/${data.id}`)
    },
    onError: (err: any) => {
      setJoinError(err.response?.data?.detail || 'Failed to join league.')
    },
  })

  const formattedLeagues = useMemo(() => {
    const query = searchInput.trim().toLowerCase()
    const filtered = query
      ? leagues.filter((league) => league.name.toLowerCase().includes(query))
      : leagues

    return filtered.map((league) => ({
      ...league,
      createdLabel: format(new Date(league.created_at), 'MMM d, yyyy'),
    }))
  }, [leagues, searchInput])

  const handleJoinClick = (league: LeagueSummary) => {
    if (league.is_member) {
      navigate(`/leagues/${league.id}`)
      return
    }
    setJoinError('')
    setJoinTarget(league)
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link
          to="/dashboard"
          className="text-sm text-primary-medium hover:text-primary-dark transition-colors"
        >
          ← Back to dashboard
        </Link>

        <h1 className="mt-4 text-2xl font-bold text-neutral-DEFAULT">Global Leagues</h1>
        <p className="mt-2 text-sm text-neutral-DEFAULT/70">
          Browse all leagues in Predico and find one to join.
        </p>

        <div className="mt-6">
          <label htmlFor="league-search" className="sr-only">
            Search for a league
          </label>
          <input
            id="league-search"
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search for a league"
            className="block w-full rounded-md border border-neutral-DEFAULT/30 bg-white px-4 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
          />
        </div>

        <div className="mt-6 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="px-4 py-8 text-center text-sm text-neutral-DEFAULT/60">Loading leagues...</div>
          ) : error ? (
            <div className="px-4 py-8 text-center text-sm text-red-600">Failed to load leagues.</div>
          ) : formattedLeagues.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-neutral-DEFAULT/60">
              No leagues found{searchInput.trim() ? ` matching "${searchInput.trim()}"` : ''}.
            </div>
          ) : (
            <table className="min-w-full divide-y divide-neutral-DEFAULT/10">
              <thead className="bg-neutral-light">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                    League Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                    Members
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                    Created
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-DEFAULT/10">
                {formattedLeagues.map((league) => (
                  <tr key={league.id} className="hover:bg-neutral-light/60 transition-colors">
                    <td className="px-4 py-3 text-sm text-neutral-DEFAULT">
                      <button
                        type="button"
                        onClick={() => navigate(`/leagues/${league.id}`)}
                        className="inline-flex items-center gap-2 hover:text-primary-medium transition-colors"
                      >
                        {league.name}
                        {league.is_private && (
                          <span title="Password protected" aria-label="Private league">
                            <svg
                              className="w-4 h-4 text-neutral-DEFAULT/60"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                              />
                            </svg>
                          </span>
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-DEFAULT">{league.member_count}</td>
                    <td className="px-4 py-3 text-sm text-neutral-DEFAULT/80">{league.createdLabel}</td>
                    <td className="px-4 py-3 text-sm text-right">
                      {league.is_member ? (
                        <button
                          type="button"
                          onClick={() => navigate(`/leagues/${league.id}`)}
                          className="text-primary-medium hover:text-primary-dark font-medium"
                        >
                          View
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleJoinClick(league)}
                          className="text-primary-medium hover:text-primary-dark font-medium"
                        >
                          Join
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {joinTarget && (
        <JoinLeagueModal
          isOpen={Boolean(joinTarget)}
          leagueName={joinTarget.name}
          requiresPassword={joinTarget.is_private}
          isSubmitting={joinMutation.isPending}
          error={joinError}
          onClose={() => setJoinTarget(null)}
          onSubmit={(password) =>
            joinMutation.mutate({ leagueId: joinTarget.id, password })
          }
        />
      )}
    </div>
  )
}
