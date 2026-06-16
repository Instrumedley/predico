import React, { useMemo } from 'react'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import { getLeagueProgressMatrixCell } from '@/utils/leagueProgressMatrix'
import { LeagueProgressResponse } from '@/services/leagues'
import { MemberFilter, resolveVisibleMembers } from './LeagueProgressChart'

interface LeagueProgressMatrixProps {
  data: LeagueProgressResponse
  variant?: 'preview' | 'fullscreen'
  memberFilter?: MemberFilter
  className?: string
}

export const LeagueProgressMatrix: React.FC<LeagueProgressMatrixProps> = ({
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

  return (
    <div className={className}>
      <div className="h-full w-full overflow-auto overscroll-contain [-webkit-overflow-scrolling:touch]">
        <table className="min-w-full border-collapse text-xs">
          <thead>
            <tr>
              <th
                className="sticky left-0 z-20 border-b border-r border-neutral-DEFAULT/15 bg-white px-3 py-2 text-left font-semibold text-neutral-DEFAULT"
                scope="col"
              >
                Player
              </th>
              {data.matches.map((match) => (
                <th
                  key={match.game_id}
                  className="border-b border-neutral-DEFAULT/15 bg-neutral-light/80 px-1 py-2 text-center align-bottom"
                  scope="col"
                  title={`${match.home_team.name} vs ${match.away_team.name}`}
                >
                  <div className="mx-auto flex w-9 flex-col items-center gap-0.5 leading-none">
                    <span
                      className={`fi fi-${getCountryCodeForFlag(match.home_team.country_code)} fis rounded-sm`}
                      style={{ fontSize: isPreview ? '0.8rem' : '0.9rem' }}
                      aria-hidden="true"
                    />
                    <span className="text-[10px] text-neutral-DEFAULT/45">×</span>
                    <span
                      className={`fi fi-${getCountryCodeForFlag(match.away_team.country_code)} fis rounded-sm`}
                      style={{ fontSize: isPreview ? '0.8rem' : '0.9rem' }}
                      aria-hidden="true"
                    />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleMembers.map((member) => (
              <tr key={member.user_id} className="group">
                <th
                  scope="row"
                  className={`sticky left-0 z-10 border-r border-neutral-DEFAULT/10 bg-white px-3 py-1.5 text-left font-medium text-neutral-DEFAULT group-hover:bg-neutral-light/60 ${
                    member.is_current_user ? 'text-primary-medium' : ''
                  }`}
                >
                  <span className="mr-2 tabular-nums text-neutral-DEFAULT/50">{member.rank}</span>
                  <span className="truncate">{member.username}</span>
                  {member.is_current_user && (
                    <span className="ml-1 text-[10px] font-normal text-neutral-DEFAULT/60">(You)</span>
                  )}
                </th>
                {data.matches.map((match, matchIndex) => {
                  const cell = getLeagueProgressMatrixCell(member.match_points?.[matchIndex])
                  return (
                    <td
                      key={`${member.user_id}-${match.game_id}`}
                      className="border-b border-neutral-DEFAULT/10 px-0.5 py-0.5 text-center"
                    >
                      <div
                        className="mx-auto flex min-h-[2rem] w-11 items-center justify-center rounded px-0.5 py-1 text-[11px] font-semibold tabular-nums"
                        style={{
                          backgroundColor: cell.backgroundColor,
                          color: cell.color,
                        }}
                        title={
                          cell.label === 'N/A'
                            ? 'No prediction submitted'
                            : `${member.username}: ${cell.label} pts`
                        }
                      >
                        <span>{cell.label}</span>
                        {cell.showBullseye && (
                          <span className="ml-0.5" aria-label="Perfect prediction">
                            🎯
                          </span>
                        )}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
