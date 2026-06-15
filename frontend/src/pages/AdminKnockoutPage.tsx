import React, { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { NavBar } from '@/components/layout/NavBar'
import { AdminSubNav } from '@/components/admin/AdminSubNav'
import { KnockoutBracket } from '@/components/knockout'
import { getAdminKnockoutBracket, updateKnockoutMatchResult } from '@/services/knockout'
import { useFeedback } from '@/contexts/FeedbackContext'
import { KnockoutSavePayload } from '@/types/knockout'

export const AdminKnockoutPage: React.FC = () => {
  const { showFeedback } = useFeedback()
  const queryClient = useQueryClient()
  const [savingMatchNumber, setSavingMatchNumber] = useState<number | null>(null)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['knockoutBracket', 'admin'],
    queryFn: getAdminKnockoutBracket,
  })

  const handleSaveMatch = async (payload: KnockoutSavePayload) => {
    setSavingMatchNumber(payload.matchNumber)
    try {
      const updated = await updateKnockoutMatchResult(payload.matchNumber, {
        homeScore: payload.homeScore,
        awayScore: payload.awayScore,
        winnerTeamId: payload.winnerTeamId,
      })
      queryClient.setQueryData(['knockoutBracket', 'admin'], updated)
      queryClient.invalidateQueries({ queryKey: ['knockoutBracket', 'public'] })
      showFeedback('Knockout result saved', 'success')
    } catch {
      showFeedback('Failed to save knockout result', 'error')
    } finally {
      setSavingMatchNumber(null)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <AdminSubNav />

        {isLoading && (
          <div className="rounded-xl border border-neutral-DEFAULT/20 bg-white px-6 py-10 text-center text-sm text-neutral-DEFAULT/70">
            Loading knockout bracket…
          </div>
        )}

        {isError && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-10 text-center text-sm text-red-700">
            Unable to load the admin knockout bracket.{' '}
            <button type="button" className="underline" onClick={() => refetch()}>
              Retry
            </button>
          </div>
        )}

        {data && (
          <KnockoutBracket
            data={data}
            admin
            savingMatchNumber={savingMatchNumber}
            onSaveMatch={handleSaveMatch}
          />
        )}
      </div>
    </div>
  )
}
