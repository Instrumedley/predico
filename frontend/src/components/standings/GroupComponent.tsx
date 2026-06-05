import React from 'react'
import { GroupStanding } from '@/types/standings'
import { abbreviateCountryName } from '@/utils/countryNames'
import { getCountryCodeForFlag } from '@/utils/countryFlags'

interface GroupComponentProps {
  group: GroupStanding
}

export const GroupComponent: React.FC<GroupComponentProps> = ({ group }) => {

  return (
    <div className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm overflow-hidden w-full min-w-[280px]">
      {/* Group Title */}
      <div className="px-4 py-2 border-b border-neutral-DEFAULT/20" style={{ backgroundColor: '#EEF8FF' }}>
        <h3 className="font-bold text-neutral-DEFAULT">Group {group.groupLetter}</h3>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs table-fixed">
          <colgroup>
            <col className="w-6" /> {/* Position */}
            <col className="w-[90px]" /> {/* Team name - fixed width */}
            <col className="w-7" /> {/* P */}
            <col className="w-7" /> {/* W */}
            <col className="w-7" /> {/* D */}
            <col className="w-7" /> {/* L */}
            <col className="w-9" /> {/* Pts */}
            <col className="w-7" /> {/* GF */}
            <col className="w-7" /> {/* GA */}
            <col className="w-8" /> {/* GD */}
          </colgroup>
          {/* Table Headers */}
          <thead className="bg-neutral-light border-b border-neutral-DEFAULT/20">
            <tr>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium"></th>
              <th className="px-1 py-1.5 text-left text-neutral-DEFAULT font-medium"></th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">P</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">W</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">D</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">L</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium font-bold">
                Pts
              </th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">GF</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">GA</th>
              <th className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">GD</th>
            </tr>
          </thead>
          <tbody>
            {group.teams.map((team) => (
              <tr
                key={team.countryCode}
                className={`border-t border-neutral-DEFAULT/10 hover:bg-neutral-light/50 transition-colors`}
              >
                {/* Position */}
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT font-medium">
                  {team.position}
                </td>
                {/* Flag + Country Name - fixed width with truncation */}
                <td className="px-1 py-1.5 overflow-hidden">
                  <div className="flex items-center space-x-1 min-w-0">
                    <span
                      className={`fi fi-${getCountryCodeForFlag(team.countryCode)} fis flex-shrink-0`}
                      style={{ fontSize: '0.9rem' }}
                    ></span>
                    <span
                      className="text-neutral-DEFAULT font-medium text-xs truncate block"
                      title={team.countryName}
                    >
                      {abbreviateCountryName(team.countryName)}
                    </span>
                  </div>
                </td>
                {/* Stats */}
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.played}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.wins}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.draws}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.losses}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT font-bold whitespace-nowrap">
                  {team.points}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.goalsFor}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.goalsAgainst}
                </td>
                <td className="px-1 py-1.5 text-center text-neutral-DEFAULT whitespace-nowrap">
                  {team.goalDifference > 0 ? '+' : ''}
                  {team.goalDifference}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

