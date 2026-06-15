import React from 'react'
import { BracketMatch, BracketSlot } from '@/types/knockout'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { abbreviateCountryName } from '@/utils/countryNames'
import type { KnockoutSavePayload } from '@/types/knockout'
import { useModal } from '@/contexts/ModalContext'

export const BRACKET_TRACK_HEIGHT = 'h-[34rem] sm:h-[36rem]'
export const BRACKET_ROUND_GAP = 'gap-2'
/** Extra inset so SF match rows don't sit flush against bracket connectors. */
export const BRACKET_CENTER_HUB_INSET = 'px-1.5'

interface BracketMatchSlotProps {
  match: BracketMatch
  size?: 'sm' | 'md' | 'lg'
  admin?: boolean
  saving?: boolean
  onSave?: (payload: { homeScore: number; awayScore: number; winnerTeamId: number }) => void | Promise<void>
}

const SLOT_WIDTHS = {
  sm: 'w-[9.25rem]',
  md: 'w-[10rem]',
  lg: 'w-[11rem]',
} as const

const FLAG_SIZES = {
  sm: '0.95rem',
  md: '1.05rem',
  lg: '1.15rem',
} as const

const TEXT_SIZES = {
  sm: 'text-[11px]',
  md: 'text-xs',
  lg: 'text-sm',
} as const

interface BracketTeamRowProps {
  slot: BracketSlot
  size: 'sm' | 'md' | 'lg'
  admin?: boolean
  selectable?: boolean
  showAdvanceCheckbox?: boolean
  selected?: boolean
  onSelect?: () => void
  scoreValue?: string
  onScoreChange?: (value: string) => void
  scoreAriaLabel?: string
}

const BracketTeamRow: React.FC<BracketTeamRowProps> = ({
  slot,
  size,
  admin = false,
  selectable = false,
  showAdvanceCheckbox = false,
  selected = false,
  onSelect,
  scoreValue,
  onScoreChange,
  scoreAriaLabel,
}) => {
  const flagSize = FLAG_SIZES[size]
  const team = slot.team
  const displayName = team ? abbreviateCountryName(team.countryName) : slot.label

  if (!team && !slot.label) {
    return (
      <div
        className={`flex min-h-[2rem] w-full items-center rounded-md border border-dashed border-neutral-DEFAULT/20 bg-white/60 px-1.5 py-1 ${TEXT_SIZES[size]}`}
        aria-hidden="true"
      />
    )
  }

  if (!team && slot.label) {
    return (
      <div
        className={`flex min-h-[2rem] w-full items-center rounded-md border border-neutral-DEFAULT/30 bg-white px-1.5 py-1 shadow-sm ${TEXT_SIZES[size]}`}
      >
        <span className="text-[10px] font-medium leading-tight text-neutral-DEFAULT/75">{slot.label}</span>
      </div>
    )
  }

  if (!team) {
    return null
  }

  return (
    <div
      className={`flex w-full items-center gap-1.5 rounded-md border border-neutral-DEFAULT/30 bg-white px-1.5 py-1 shadow-sm ${TEXT_SIZES[size]} ${
        admin && selected ? 'border-primary-medium ring-1 ring-primary-medium/40' : ''
      }`}
    >
      <span
        className={`fi fi-${getCountryCodeForFlag(team.countryCode)} fis shrink-0 rounded-sm`}
        style={{ fontSize: flagSize, width: flagSize, lineHeight: flagSize }}
        title={team.countryName}
        aria-hidden="true"
      />
      <span className="min-w-0 flex-1 truncate font-medium text-neutral-DEFAULT" title={team.countryName}>
        {displayName}
      </span>
      {admin && selectable && onScoreChange && (
        <input
          type="text"
          inputMode="numeric"
          value={scoreValue ?? ''}
          onChange={(event) => onScoreChange(event.target.value.replace(/\D/g, '').slice(0, 2))}
          className="box-border h-4 w-4 shrink-0 appearance-none rounded border border-neutral-DEFAULT/30 bg-white p-0 text-center text-[10px] leading-none text-neutral-DEFAULT/70 focus:border-neutral-DEFAULT/40 focus:outline-none"
          aria-label={scoreAriaLabel}
        />
      )}
      {admin && selectable && showAdvanceCheckbox && onSelect && (
        <button
          type="button"
          onClick={onSelect}
          className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
            selected
              ? 'border-primary-medium bg-primary-medium text-white'
              : 'border-neutral-DEFAULT/30 bg-white text-transparent'
          }`}
          aria-label={`Select ${team.countryName} to advance`}
          title="Select to advance"
        >
          ✓
        </button>
      )}
    </div>
  )
}

const parseScoreValue = (value: string): number | null => {
  if (value === '') {
    return null
  }
  const parsed = Number.parseInt(value, 10)
  return Number.isNaN(parsed) ? null : parsed
}

const SAVE_CONFIRM_DELAY_MS = 800

export const BracketMatchSlot: React.FC<BracketMatchSlotProps> = ({
  match,
  size = 'sm',
  admin = false,
  saving = false,
  onSave,
}) => {
  const { showConfirm } = useModal()
  const bothTeamsKnown = Boolean(match.home.team && match.away.team)
  const [homeScore, setHomeScore] = React.useState(match.homeScore?.toString() ?? '')
  const [awayScore, setAwayScore] = React.useState(match.awayScore?.toString() ?? '')
  const [winnerTeamId, setWinnerTeamId] = React.useState<number | null>(match.winnerTeamId ?? null)
  const previousScoresRef = React.useRef({ home: homeScore, away: awayScore })
  const dismissedConfirmKeyRef = React.useRef<string | null>(null)

  const parsedHome = parseScoreValue(homeScore)
  const parsedAway = parseScoreValue(awayScore)
  const scoresValid = parsedHome !== null && parsedAway !== null
  const isDraw = scoresValid && parsedHome === parsedAway
  const savedHomeScore = match.homeScore?.toString() ?? ''
  const savedAwayScore = match.awayScore?.toString() ?? ''
  const savedWinnerTeamId = match.winnerTeamId ?? null
  const isDirty =
    homeScore !== savedHomeScore ||
    awayScore !== savedAwayScore ||
    winnerTeamId !== savedWinnerTeamId
  const canSave = scoresValid && winnerTeamId != null

  React.useEffect(() => {
    setHomeScore(match.homeScore?.toString() ?? '')
    setAwayScore(match.awayScore?.toString() ?? '')
    setWinnerTeamId(match.winnerTeamId ?? null)
    previousScoresRef.current = {
      home: match.homeScore?.toString() ?? '',
      away: match.awayScore?.toString() ?? '',
    }
  }, [match.homeScore, match.awayScore, match.winnerTeamId])

  React.useEffect(() => {
    if (!bothTeamsKnown) {
      return
    }

    const home = parseScoreValue(homeScore)
    const away = parseScoreValue(awayScore)
    const previousHome = parseScoreValue(previousScoresRef.current.home)
    const previousAway = parseScoreValue(previousScoresRef.current.away)
    const wasNotDraw =
      previousHome !== null && previousAway !== null && previousHome !== previousAway

    if (home === null || away === null) {
      setWinnerTeamId(null)
      previousScoresRef.current = { home: homeScore, away: awayScore }
      return
    }

    if (home === away) {
      if (wasNotDraw) {
        setWinnerTeamId(null)
      }
      previousScoresRef.current = { home: homeScore, away: awayScore }
      return
    }

    if (home > away && match.home.team) {
      setWinnerTeamId(match.home.team.teamId)
    } else if (away > home && match.away.team) {
      setWinnerTeamId(match.away.team.teamId)
    }

    previousScoresRef.current = { home: homeScore, away: awayScore }
  }, [homeScore, awayScore, bothTeamsKnown, match.home.team, match.away.team])

  React.useEffect(() => {
    dismissedConfirmKeyRef.current = null
  }, [homeScore, awayScore, winnerTeamId])

  React.useEffect(() => {
    if (!admin || !onSave || !bothTeamsKnown || !canSave || !isDirty || saving) {
      return
    }

    const confirmKey = `${match.matchNumber}:${homeScore}:${awayScore}:${winnerTeamId}`
    if (dismissedConfirmKeyRef.current === confirmKey) {
      return
    }

    const timer = window.setTimeout(() => {
      const homeName = abbreviateCountryName(match.home.team!.countryName)
      const awayName = abbreviateCountryName(match.away.team!.countryName)
      const winnerName =
        winnerTeamId === match.home.team?.teamId
          ? homeName
          : winnerTeamId === match.away.team?.teamId
            ? awayName
            : 'Winner'

      showConfirm(
        'Save knockout result?',
        `${homeName} ${parsedHome} – ${parsedAway} ${awayName}\n\n${winnerName} advances to the next round.`,
        async () => {
          await onSave({
            homeScore: parsedHome!,
            awayScore: parsedAway!,
            winnerTeamId: winnerTeamId!,
          })
        },
        'Save',
        'Cancel',
        () => {
          dismissedConfirmKeyRef.current = confirmKey
        }
      )
    }, SAVE_CONFIRM_DELAY_MS)

    return () => window.clearTimeout(timer)
  }, [
    admin,
    onSave,
    bothTeamsKnown,
    canSave,
    isDirty,
    saving,
    homeScore,
    awayScore,
    winnerTeamId,
    match.matchNumber,
    match.home.team,
    match.away.team,
    parsedHome,
    parsedAway,
    showConfirm,
  ])

  return (
    <div
      className={`flex flex-col gap-1.5 ${SLOT_WIDTHS[size]} ${saving ? 'opacity-60' : ''}`}
    >
      <BracketTeamRow
        slot={match.home}
        size={size}
        admin={admin}
        selectable={admin && bothTeamsKnown}
        showAdvanceCheckbox={isDraw}
        selected={winnerTeamId === match.home.team?.teamId}
        onSelect={() => match.home.team && setWinnerTeamId(match.home.team.teamId)}
        scoreValue={homeScore}
        onScoreChange={setHomeScore}
        scoreAriaLabel={`${match.home.team?.countryName ?? 'Home'} score`}
      />
      <BracketTeamRow
        slot={match.away}
        size={size}
        admin={admin}
        selectable={admin && bothTeamsKnown}
        showAdvanceCheckbox={isDraw}
        selected={winnerTeamId === match.away.team?.teamId}
        onSelect={() => match.away.team && setWinnerTeamId(match.away.team.teamId)}
        scoreValue={awayScore}
        onScoreChange={setAwayScore}
        scoreAriaLabel={`${match.away.team?.countryName ?? 'Away'} score`}
      />
    </div>
  )
}

interface BracketRoundColumnProps {
  label: string
  matches: BracketMatch[]
  size?: 'sm' | 'md' | 'lg'
  singleMatch?: boolean
  admin?: boolean
  savingMatchNumber?: number | null
  onSaveMatch?: (payload: KnockoutSavePayload) => void | Promise<void>
}

export const BracketRoundColumn: React.FC<BracketRoundColumnProps> = ({
  label,
  matches,
  size = 'sm',
  singleMatch = false,
  admin = false,
  savingMatchNumber = null,
  onSaveMatch,
}) => (
  <div className={`flex shrink-0 flex-col items-stretch ${SLOT_WIDTHS[size]}`}>
    <span className="mb-2 text-center text-[10px] font-semibold uppercase tracking-wide text-neutral-DEFAULT/60">
      {label}
    </span>
    <div
      className={`flex ${BRACKET_TRACK_HEIGHT} flex-col py-1 ${
        singleMatch ? 'justify-center' : 'justify-around'
      }`}
    >
      {matches.map((match) => (
        <BracketMatchSlot
          key={match.matchNumber}
          match={match}
          size={size}
          admin={admin}
          saving={savingMatchNumber === match.matchNumber}
          onSave={
            onSaveMatch
              ? (payload) => onSaveMatch({ ...payload, matchNumber: match.matchNumber })
              : undefined
          }
        />
      ))}
    </div>
  </div>
)

interface BracketConnectorProps {
  direction: 'left' | 'right'
}

export const BracketConnector: React.FC<BracketConnectorProps> = ({ direction }) => (
  <div className="relative hidden w-8 shrink-0 self-stretch sm:block" aria-hidden="true">
    <div
      className={`absolute inset-y-[8%] w-1/2 border-primary-medium/25 ${
        direction === 'left'
          ? 'right-0 rounded-r-md border-r border-t border-b'
          : 'left-0 rounded-l-md border-l border-t border-b'
      }`}
    />
  </div>
)
