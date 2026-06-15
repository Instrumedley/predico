import React from 'react'
import { BracketMatch, BracketSideData, KnockoutSavePayload } from '@/types/knockout'
import {
  BRACKET_TRACK_HEIGHT,
  BracketConnector,
  BracketMatchSlot,
  BracketRoundColumn,
} from './BracketMatchSlot'

interface BracketOuterRoundsProps {
  side: BracketSideData
  direction: 'left' | 'right'
  admin?: boolean
  savingMatchNumber?: number | null
  onSaveMatch?: (payload: KnockoutSavePayload) => void
}

const OUTER_ROUNDS = [
  { label: 'R32', key: 'r32', getMatches: (side: BracketSideData) => side.roundOf32 },
  { label: 'R16', key: 'r16', getMatches: (side: BracketSideData) => side.roundOf16 },
  { label: 'QF', key: 'qf', getMatches: (side: BracketSideData) => side.quarterFinals },
] as const

export const BracketOuterRounds: React.FC<BracketOuterRoundsProps> = ({
  side,
  direction,
  admin = false,
  savingMatchNumber = null,
  onSaveMatch,
}) => {
  const rounds = direction === 'left' ? OUTER_ROUNDS : [...OUTER_ROUNDS].reverse()

  return (
    <div className="flex shrink-0 items-start">
      {rounds.map((round, index) => (
        <React.Fragment key={round.key}>
          <BracketRoundColumn
            label={round.label}
            matches={round.getMatches(side)}
            admin={admin}
            savingMatchNumber={savingMatchNumber}
            onSaveMatch={onSaveMatch}
          />
          {index < rounds.length - 1 && <BracketConnector direction={direction} />}
        </React.Fragment>
      ))}
    </div>
  )
}

interface BracketCenterHubProps {
  leftSemiFinal: BracketMatch
  rightSemiFinal: BracketMatch
  final: BracketMatch
  admin?: boolean
  savingMatchNumber?: number | null
  onSaveMatch?: (payload: KnockoutSavePayload) => void
}

export const BracketCenterHub: React.FC<BracketCenterHubProps> = ({
  leftSemiFinal,
  rightSemiFinal,
  final,
  admin = false,
  savingMatchNumber = null,
  onSaveMatch,
}) => (
  <div className="flex shrink-0 items-start border-x border-neutral-DEFAULT/10 px-3 sm:px-4">
    <BracketRoundColumn
      label="SF"
      matches={[leftSemiFinal]}
      size="md"
      singleMatch
      admin={admin}
      savingMatchNumber={savingMatchNumber}
      onSaveMatch={onSaveMatch}
    />
    <BracketConnector direction="left" />

    <div className="flex w-[11rem] shrink-0 flex-col items-stretch">
      <span className="mb-2 text-center text-[10px] font-semibold uppercase tracking-[0.2em] text-primary-medium">
        Final
      </span>
      <div className={`flex ${BRACKET_TRACK_HEIGHT} flex-col items-center justify-center gap-3 py-1`}>
        <BracketMatchSlot
          match={final}
          size="lg"
          admin={admin}
          saving={savingMatchNumber === final.matchNumber}
          onSave={
            onSaveMatch
              ? (payload) => onSaveMatch({ ...payload, matchNumber: final.matchNumber })
              : undefined
          }
        />
        <div className="flex flex-col items-center gap-1">
          <span className="text-3xl sm:text-4xl" aria-hidden="true">
            🏆
          </span>
          <span className="text-center text-[10px] font-semibold uppercase tracking-[0.18em] text-neutral-DEFAULT/60">
            World Champions
          </span>
        </div>
      </div>
    </div>

    <BracketConnector direction="right" />

    <BracketRoundColumn
      label="SF"
      matches={[rightSemiFinal]}
      size="md"
      singleMatch
      admin={admin}
      savingMatchNumber={savingMatchNumber}
      onSaveMatch={onSaveMatch}
    />
  </div>
)

interface BracketThirdPlaceProps {
  match: BracketMatch
  admin?: boolean
  savingMatchNumber?: number | null
  onSaveMatch?: (payload: KnockoutSavePayload) => void
}

export const BracketThirdPlace: React.FC<BracketThirdPlaceProps> = ({
  match,
  admin = false,
  savingMatchNumber = null,
  onSaveMatch,
}) => (
  <div className="mt-5 flex flex-col items-center gap-2">
    <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-neutral-DEFAULT/60">
      3rd Place
    </span>
    <BracketMatchSlot
      match={match}
      size="md"
      admin={admin}
      saving={savingMatchNumber === match.matchNumber}
      onSave={
        onSaveMatch
          ? (payload) => onSaveMatch({ ...payload, matchNumber: match.matchNumber })
          : undefined
      }
    />
  </div>
)
