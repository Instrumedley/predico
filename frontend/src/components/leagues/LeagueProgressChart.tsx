import React, { useMemo } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { LeagueProgressMember, LeagueProgressMatch, LeagueProgressResponse } from '@/services/leagues'

const LINE_COLORS = ['#1d4ed8', '#be123c', '#059669', '#d97706', '#7c3aed']
const EXTENDED_LINE_COLORS = [
  '#1d4ed8',
  '#be123c',
  '#059669',
  '#d97706',
  '#7c3aed',
  '#0891b2',
  '#c026d3',
  '#65a30d',
  '#ea580c',
  '#4f46e5',
  '#db2777',
  '#0d9488',
  '#ca8a04',
  '#9333ea',
  '#2563eb',
]
const CURRENT_USER_COLOR = '#0f766e'

/** Rank bands 1-5, 6-10, 11-15, 16-20 — greens, oranges, blues, purples. */
export const RANK_CLUSTER_COLORS: readonly (readonly string[])[] = [
  ['#8DB600', '#0BDA51', '#22C55E', '#009E60', '#84CC16'],
  ['#FFBF00', '#FFD700', '#FF9F00', '#C04000', '#DC2626'],
  ['#007FFF', '#06B6D4', '#6CB4EE', '#008080', '#40E0D0'],
  ['#9966CC', '#FBAED2', '#A855F7', '#D946EF', '#7E22CE'],
]

export function shouldUseRankClusterColors(memberCount: number): boolean {
  return memberCount > 10
}

export function getRankClusterColor(rank: number): string {
  if (rank < 1) {
    return LINE_COLORS[0]
  }

  const clusterIndex = Math.min(
    Math.floor((rank - 1) / 5),
    RANK_CLUSTER_COLORS.length - 1
  )
  const shadeIndex = (rank - 1) % 5

  return RANK_CLUSTER_COLORS[clusterIndex][shadeIndex]
}

export type MemberFilter = 'all' | 'top5'

export interface ChartRow {
  key: string
  label: string
  match?: LeagueProgressMatch
  [dataKey: string]: string | number | LeagueProgressMatch | undefined
}

export function getVisibleMembers(members: LeagueProgressMember[]): LeagueProgressMember[] {
  const topFive = members.filter((member) => member.is_top_five)
  const currentUser = members.find((member) => member.is_current_user)
  const visible = [...topFive]

  if (currentUser && !visible.some((member) => member.user_id === currentUser.user_id)) {
    visible.push(currentUser)
  }

  return visible.sort((a, b) => a.rank - b.rank)
}

export function resolveVisibleMembers(
  members: LeagueProgressMember[],
  filter: MemberFilter
): LeagueProgressMember[] {
  if (filter === 'all') {
    return [...members].sort((a, b) => a.rank - b.rank)
  }
  return getVisibleMembers(members)
}

export function buildChartData(
  progress: LeagueProgressResponse,
  visibleMembers: LeagueProgressMember[]
): ChartRow[] {
  const rows: ChartRow[] = [{ key: 'start', label: 'Start' }]

  visibleMembers.forEach((member) => {
    rows[0][`u${member.user_id}`] = member.points[0] ?? 0
  })

  progress.matches.forEach((match, index) => {
    const row: ChartRow = {
      key: `match-${match.game_id}`,
      label: match.label,
      match,
    }

    visibleMembers.forEach((member) => {
      row[`u${member.user_id}`] = member.points[index + 1] ?? member.points[index] ?? 0
    })

    rows.push(row)
  })

  return rows
}

function getMemberColor(
  member: LeagueProgressMember,
  paletteIndex: number,
  memberCount: number,
  showAllMembers: boolean
): string {
  if (shouldUseRankClusterColors(memberCount)) {
    return getRankClusterColor(member.rank)
  }

  if (member.is_current_user) {
    return CURRENT_USER_COLOR
  }

  const palette = showAllMembers ? EXTENDED_LINE_COLORS : LINE_COLORS
  return palette[paletteIndex % palette.length]
}

interface ProgressTooltipProps {
  active?: boolean
  payload?: Array<{ dataKey: string; value: number; color: string; name: string }>
  label?: string
  chartRows: ChartRow[]
}

const ProgressTooltip: React.FC<ProgressTooltipProps> = ({ active, payload, label, chartRows }) => {
  if (!active || !payload?.length) {
    return null
  }

  const row = chartRows.find((entry) => entry.label === label)
  const match = row?.match

  return (
    <div className="rounded-lg border border-neutral-DEFAULT/10 bg-white px-4 py-3 shadow-lg">
      {match ? (
        <div className="mb-3 flex items-center gap-2 text-sm font-medium text-neutral-DEFAULT">
          <span
            className={`fi fi-${getCountryCodeForFlag(match.home_team.country_code)} fis rounded-sm`}
            aria-hidden="true"
          />
          <span className="text-neutral-DEFAULT/60">vs</span>
          <span
            className={`fi fi-${getCountryCodeForFlag(match.away_team.country_code)} fis rounded-sm`}
            aria-hidden="true"
          />
          <span className="ml-1 text-neutral-DEFAULT/70">
            {match.home_team.name} vs {match.away_team.name}
          </span>
        </div>
      ) : (
        <p className="mb-3 text-sm font-medium text-neutral-DEFAULT">Before the first scored match</p>
      )}

      <ul className="space-y-1">
        {payload
          .filter((entry) => typeof entry.value === 'number')
          .sort((a, b) => b.value - a.value)
          .map((entry) => (
            <li key={entry.dataKey} className="flex items-center justify-between gap-6 text-sm">
              <span className="flex items-center gap-2 text-neutral-DEFAULT">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name}
              </span>
              <span className="font-semibold tabular-nums text-neutral-DEFAULT">{entry.value} pts</span>
            </li>
          ))}
      </ul>
    </div>
  )
}

interface LeagueProgressChartProps {
  data: LeagueProgressResponse
  variant?: 'preview' | 'fullscreen'
  memberFilter?: MemberFilter
  className?: string
}

export const LeagueProgressChart: React.FC<LeagueProgressChartProps> = ({
  data,
  variant = 'fullscreen',
  memberFilter,
  className,
}) => {
  const isPreview = variant === 'preview'
  const effectiveFilter = memberFilter ?? (isPreview ? 'top5' : 'all')

  const visibleMembers = useMemo(
    () => resolveVisibleMembers(data.members, effectiveFilter),
    [data.members, effectiveFilter]
  )
  const chartData = useMemo(
    () => buildChartData(data, visibleMembers),
    [data, visibleMembers]
  )

  const tickInterval = useMemo(() => {
    const targetTicks = isPreview ? 8 : 14
    if (chartData.length <= targetTicks) {
      return 0
    }
    return Math.max(1, Math.floor(chartData.length / targetTicks))
  }, [chartData.length, isPreview])

  // Keep enough horizontal space per match so linear segments stay visibly diagonal
  // on narrow screens instead of looking like step lines.
  const minChartWidth = useMemo(() => {
    const pixelsPerPoint = isPreview ? 28 : 24
    const baseMinWidth = isPreview ? 280 : 360
    return Math.max(baseMinWidth, chartData.length * pixelsPerPoint)
  }, [chartData.length, isPreview])

  return (
    <div className={className}>
      <div className="h-full w-full overflow-x-auto overflow-y-hidden overscroll-x-contain [-webkit-overflow-scrolling:touch]">
        <div className="h-full" style={{ width: `max(100%, ${minChartWidth}px)` }}>
          <ResponsiveContainer width="100%" height="100%" minHeight={isPreview ? 300 : 420}>
            <LineChart
              data={chartData}
              margin={{
                top: isPreview ? 8 : 12,
                right: isPreview ? 12 : 24,
                left: isPreview ? 0 : 4,
                bottom: isPreview ? 48 : 56,
              }}
            >
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fontSize: isPreview ? 10 : 11, fill: '#6b7280' }}
                interval={tickInterval}
                angle={isPreview ? -40 : -35}
                textAnchor="end"
                height={isPreview ? 56 : 70}
              />
              <YAxis
                tick={{ fontSize: isPreview ? 10 : 12, fill: '#6b7280' }}
                allowDecimals={false}
                width={isPreview ? 36 : 48}
                label={
                  isPreview
                    ? undefined
                    : {
                        value: 'Points',
                        angle: -90,
                        position: 'insideLeft',
                        fill: '#6b7280',
                        style: { textAnchor: 'middle' },
                      }
                }
              />
              <Tooltip content={<ProgressTooltip chartRows={chartData} />} />
              <Legend
                verticalAlign="bottom"
                height={isPreview ? 36 : 48}
                wrapperStyle={{ paddingTop: isPreview ? 8 : 16 }}
                iconSize={isPreview ? 8 : 14}
                formatter={(value) => {
                  const member = visibleMembers.find((item) => item.username === value)
                  if (member?.is_current_user) {
                    return `${value} (You)`
                  }
                  return String(value)
                }}
              />
              {visibleMembers.map((member, index) => (
                <Line
                  key={member.user_id}
                  type="linear"
                  dataKey={`u${member.user_id}`}
                  name={member.username}
                  stroke={getMemberColor(
                    member,
                    index,
                    visibleMembers.length,
                    effectiveFilter === 'all'
                  )}
                  strokeWidth={member.is_current_user ? (isPreview ? 2.5 : 3.5) : isPreview ? 2 : 2.5}
                  dot={false}
                  activeDot={{ r: member.is_current_user ? (isPreview ? 4 : 6) : isPreview ? 3 : 5 }}
                  isAnimationActive={!isPreview}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
