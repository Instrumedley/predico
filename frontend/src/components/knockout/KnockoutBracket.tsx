import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { KnockoutBracketData } from '@/types/knockout'
import { getKnockoutBracket } from '@/services/knockout'
import { BracketCenterHub, BracketOuterRounds, BracketThirdPlace } from './BracketSide'
import { BRACKET_ROUND_GAP, BracketConnector } from './BracketMatchSlot'
import type { KnockoutSavePayload } from '@/types/knockout'

interface KnockoutBracketProps {
  data?: KnockoutBracketData
  admin?: boolean
  savingMatchNumber?: number | null
  onSaveMatch?: (payload: KnockoutSavePayload) => void
}

export const KnockoutBracket: React.FC<KnockoutBracketProps> = ({
  data: dataProp,
  admin = false,
  savingMatchNumber = null,
  onSaveMatch,
}) => {
  const { data: fetchedData, isLoading, isError } = useQuery({
    queryKey: ['knockoutBracket', admin ? 'admin' : 'public'],
    queryFn: admin ? undefined : getKnockoutBracket,
    enabled: !dataProp && !admin,
  })

  const data = dataProp ?? fetchedData

  return (
    <div className="w-full">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-neutral-DEFAULT">Knockout Stage</h2>
        <p className="mt-1 text-sm text-neutral-DEFAULT/70">
          {admin
            ? 'Record full-time scores and select which team advances (including after extra time or penalties).'
            : 'FIFA World Cup 2026 — bracket updates as group standings and knockout results are confirmed.'}
        </p>
        {data?.thirdPlaceCombinationKey && (
          <p className="mt-1 text-xs text-neutral-DEFAULT/55">
            Third-place combination: {data.thirdPlaceCombinationKey}
          </p>
        )}
      </div>

      {!dataProp && !admin && isLoading && (
        <div className="rounded-xl border border-neutral-DEFAULT/20 bg-white px-6 py-10 text-center text-sm text-neutral-DEFAULT/70">
          Loading knockout bracket…
        </div>
      )}

      {!dataProp && !admin && isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-10 text-center text-sm text-red-700">
          Unable to load the knockout bracket.
        </div>
      )}

      {data && (
        <div className="overflow-x-auto overscroll-x-contain rounded-xl border border-neutral-DEFAULT/20 bg-neutral-light/50 shadow-sm [-webkit-overflow-scrolling:touch]">
          <div className="inline-flex min-w-full justify-center px-3 py-5 sm:px-4 sm:py-6">
            <div className="inline-flex min-w-max flex-col items-center rounded-lg bg-[linear-gradient(90deg,#ffffff_0%,rgba(149,224,108,0.07)_18%,rgba(149,224,108,0.13)_50%,rgba(149,224,108,0.07)_82%,#ffffff_100%)] px-3 py-5 sm:px-6 sm:py-6">
              <div className="inline-flex min-w-max items-start">
                <div className="flex min-w-fit flex-1 justify-end">
                  <BracketOuterRounds
                    side={data.left}
                    direction="left"
                    admin={admin}
                    savingMatchNumber={savingMatchNumber}
                    onSaveMatch={onSaveMatch}
                  />
                  <BracketConnector direction="left" />
                </div>

                <BracketCenterHub
                  leftSemiFinal={data.left.semiFinal}
                  rightSemiFinal={data.right.semiFinal}
                  final={data.final}
                  admin={admin}
                  savingMatchNumber={savingMatchNumber}
                  onSaveMatch={onSaveMatch}
                />

                <div className="flex min-w-fit flex-1 justify-start">
                  <BracketConnector direction="right" />
                  <BracketOuterRounds
                    side={data.right}
                    direction="right"
                    admin={admin}
                    savingMatchNumber={savingMatchNumber}
                    onSaveMatch={onSaveMatch}
                  />
                </div>
              </div>

              <BracketThirdPlace
                match={data.thirdPlace}
                admin={admin}
                savingMatchNumber={savingMatchNumber}
                onSaveMatch={onSaveMatch}
              />
            </div>
          </div>
        </div>
      )}

      <p className="mt-3 text-xs text-neutral-DEFAULT/55 sm:hidden">
        Swipe horizontally to explore the full bracket.
      </p>
    </div>
  )
}
