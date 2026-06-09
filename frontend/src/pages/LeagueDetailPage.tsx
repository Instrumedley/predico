import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { NavBar } from '@/components/layout'
import { JoinLeagueModal } from '@/components/leagues'
import { useAuth } from '@/contexts/AuthContext'
import { useFeedback } from '@/contexts/FeedbackContext'
import {
  acceptLeagueInvite,
  getLeagueDetail,
  inviteToLeague,
  joinLeague,
  parseEmailInput,
} from '@/services/leagues'

export const LeagueDetailPage: React.FC = () => {
  const { leagueId } = useParams<{ leagueId: string }>()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const { showFeedback } = useFeedback()
  const inviteToken = searchParams.get('invite')
  const handledInviteToken = useRef<string | null>(null)

  const leaguePublicId = leagueId ?? ''
  const [joinOpen, setJoinOpen] = useState(false)
  const [joinError, setJoinError] = useState('')
  const [inviteInput, setInviteInput] = useState('')
  const [inviteError, setInviteError] = useState('')

  const { data: league, isLoading, error } = useQuery({
    queryKey: ['leagueDetail', leaguePublicId],
    queryFn: () => getLeagueDetail(leaguePublicId),
    enabled: Boolean(leaguePublicId),
  })

  const joinMutation = useMutation({
    mutationFn: (password?: string) => joinLeague(leaguePublicId, password),
    onSuccess: (data) => {
      setJoinOpen(false)
      setJoinError('')
      queryClient.setQueryData(['leagueDetail', leaguePublicId], data)
      queryClient.invalidateQueries({ queryKey: ['myLeagues'] })
      queryClient.invalidateQueries({ queryKey: ['allLeagues'] })
      showFeedback(`You joined ${data.name}.`, 'success')
    },
    onError: (err: any) => {
      setJoinError(err.response?.data?.detail || 'Failed to join league.')
    },
  })

  const inviteMutation = useMutation({
    mutationFn: (emails: string[]) => inviteToLeague(leaguePublicId, emails),
    onSuccess: (result) => {
      setInviteInput('')
      setInviteError('')
      if (result.sent.length > 0) {
        showFeedback(
          `Invitation${result.sent.length > 1 ? 's' : ''} sent to ${result.sent.length} email address${result.sent.length > 1 ? 'es' : ''}.`,
          'success'
        )
      }
      if (result.failed.length > 0) {
        showFeedback(`Could not send to: ${result.failed.join(', ')}`, 'error')
      }
    },
    onError: (err: any) => {
      setInviteError(err.response?.data?.detail || 'Failed to send invitations.')
    },
  })

  const acceptInviteMutation = useMutation({
    mutationFn: (token: string) => acceptLeagueInvite(token),
    onSuccess: (data) => {
      queryClient.setQueryData(['leagueDetail', leaguePublicId], data)
      queryClient.invalidateQueries({ queryKey: ['myLeagues'] })
      queryClient.invalidateQueries({ queryKey: ['allLeagues'] })
      showFeedback(`You joined ${data.name}!`, 'success')
      if (searchParams.has('invite')) {
        const nextParams = new URLSearchParams(searchParams)
        nextParams.delete('invite')
        setSearchParams(nextParams, { replace: true })
      }
    },
    onError: (err: any) => {
      showFeedback(err.response?.data?.detail || 'Could not accept this invitation.', 'error')
    },
  })

  useEffect(() => {
    if (!inviteToken || !league || league.is_member) {
      return
    }
    if (handledInviteToken.current === inviteToken) {
      return
    }
    handledInviteToken.current = inviteToken
    acceptInviteMutation.mutate(inviteToken)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inviteToken, league?.is_member, league?.id])

  const parsedEmails = useMemo(() => parseEmailInput(inviteInput), [inviteInput])
  const createdLabel = league ? format(new Date(league.created_at), 'MMM d, yyyy') : ''

  const handleJoinClick = () => {
    if (!league) return
    setJoinError('')
    if (league.is_private) {
      setJoinOpen(true)
      return
    }
    joinMutation.mutate(undefined)
  }

  const handleInviteSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setInviteError('')
    if (parsedEmails.length === 0) {
      setInviteError('Enter at least one valid email address.')
      return
    }
    inviteMutation.mutate(parsedEmails)
  }

  if (!leaguePublicId) {
    return (
      <div className="min-h-screen bg-neutral-light">
        <NavBar />
        <div className="max-w-4xl mx-auto px-4 py-8 text-sm text-red-600">Invalid league.</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="text-sm text-primary-medium hover:text-primary-dark transition-colors"
        >
          ← Back
        </button>

        {isLoading ? (
          <div className="mt-6 text-sm text-neutral-DEFAULT/60">Loading league...</div>
        ) : error || !league ? (
          <div className="mt-6 text-sm text-red-600">League not found.</div>
        ) : (
          <>
            <div className="mt-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex min-w-0 flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold text-neutral-DEFAULT">{league.name}</h1>
                  {league.is_private && (
                    <span className="inline-flex items-center rounded-full bg-neutral-light px-2 py-0.5 text-xs text-neutral-DEFAULT/70">
                      Private
                    </span>
                  )}
                </div>

                {!league.is_member && (
                  <button
                    type="button"
                    onClick={handleJoinClick}
                    disabled={joinMutation.isPending}
                    className="inline-flex shrink-0 items-center gap-2 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
                  >
                    <svg
                      className="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                      />
                    </svg>
                    {joinMutation.isPending ? 'Joining...' : 'Join'}
                  </button>
                )}
              </div>
              {league.description && (
                <p className="mt-2 text-sm text-neutral-DEFAULT/70">{league.description}</p>
              )}
              <p className="mt-2 text-xs text-neutral-DEFAULT/60">
                {league.member_count} member{league.member_count === 1 ? '' : 's'} · Created {createdLabel}
              </p>
            </div>

            {league.is_member && (
              <div className="mt-8 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm overflow-hidden">
                <div className="px-4 py-3 border-b border-neutral-DEFAULT/10 bg-neutral-light">
                  <h2 className="text-sm font-semibold text-neutral-DEFAULT">League ranking</h2>
                </div>
                {league.rankings.length === 0 ? (
                  <div className="px-4 py-8 text-center text-sm text-neutral-DEFAULT/60">
                    No points scored yet. Rankings update when match results are entered.
                  </div>
                ) : (
                  <table className="min-w-full divide-y divide-neutral-DEFAULT/10">
                    <thead>
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                          Rank
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                          Player
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-neutral-DEFAULT/70">
                          Points
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-DEFAULT/10">
                      {league.rankings.map((entry) => {
                        const isCurrentUser = user?.id === entry.user_id
                        return (
                          <tr
                            key={entry.user_id}
                            className={isCurrentUser ? 'bg-primary-medium/10' : undefined}
                          >
                            <td className="px-4 py-3 text-sm text-neutral-DEFAULT">{entry.rank}</td>
                            <td className="px-4 py-3 text-sm text-neutral-DEFAULT">
                              {entry.username}
                              {isCurrentUser && (
                                <span className="ml-2 text-xs text-primary-medium">You</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-sm text-neutral-DEFAULT text-right font-medium">
                              {entry.total_points}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {league.is_creator && (
              <div className="mt-8 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
                <h2 className="text-lg font-semibold text-neutral-DEFAULT">Invite friends</h2>
                <p className="mt-2 text-sm text-neutral-DEFAULT/70">
                  Add one or more email addresses separated by commas or new lines. Each person will
                  receive a link to this league.
                </p>

                <form onSubmit={handleInviteSubmit} className="mt-4 space-y-4">
                  <div>
                    <label htmlFor="invite-emails" className="sr-only">
                      Email addresses
                    </label>
                    <textarea
                      id="invite-emails"
                      rows={4}
                      value={inviteInput}
                      onChange={(event) => setInviteInput(event.target.value)}
                      className="block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
                    />
                    {parsedEmails.length > 0 && (
                      <p className="mt-2 text-xs text-neutral-DEFAULT/60">
                        Ready to send to {parsedEmails.length} address{parsedEmails.length === 1 ? '' : 'es'}.
                      </p>
                    )}
                  </div>

                  {inviteError && (
                    <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{inviteError}</div>
                  )}

                  <button
                    type="submit"
                    disabled={inviteMutation.isPending || parsedEmails.length === 0}
                    className="rounded-md bg-primary-medium px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-50"
                  >
                    {inviteMutation.isPending ? 'Sending invites...' : 'Send invites'}
                  </button>
                </form>
              </div>
            )}

            {!league.is_member && joinError && (
              <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{joinError}</div>
            )}

            {!league.is_member && (
              <div className="mt-8 rounded-lg border border-dashed border-neutral-DEFAULT/20 bg-white p-6 text-sm text-neutral-DEFAULT/70">
                Join this league to see the member ranking and compete with friends.
              </div>
            )}
          </>
        )}
      </div>

      {league && (
        <JoinLeagueModal
          isOpen={joinOpen}
          leagueName={league.name}
          requiresPassword={league.is_private}
          isSubmitting={joinMutation.isPending}
          error={joinError}
          onClose={() => setJoinOpen(false)}
          onSubmit={(password) => joinMutation.mutate(password)}
        />
      )}
    </div>
  )
}
