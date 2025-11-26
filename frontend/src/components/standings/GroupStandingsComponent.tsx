import React from 'react'
import { GroupComponent } from './GroupComponent'
import { StandingsData } from '@/types/standings'
import { mockStandingsData } from '@/data/mockStandings'

interface GroupStandingsComponentProps {
  standings?: StandingsData // Optional prop for when we integrate with backend
}

export const GroupStandingsComponent: React.FC<GroupStandingsComponentProps> = ({
  standings,
}) => {
  // Use provided standings or fall back to mock data
  // TODO: Replace with API call when backend is ready
  const data = standings || mockStandingsData

  // Split groups into three rows: A-D (first row), E-H (second row), I-L (third row)
  const firstRowGroups = data.groups.slice(0, 4) // Groups A-D
  const secondRowGroups = data.groups.slice(4, 8) // Groups E-H
  const thirdRowGroups = data.groups.slice(8, 12) // Groups I-L

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-neutral-DEFAULT mb-2">Group Stage Standings</h2>
        <p className="text-sm text-neutral-DEFAULT/70">
          World Cup 2026 - {data.groups.length} Groups
        </p>
      </div>

      {/* First Row: Groups A-D */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {firstRowGroups.map((group) => (
          <GroupComponent key={group.groupLetter} group={group} />
        ))}
      </div>

      {/* Second Row: Groups E-H */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {secondRowGroups.map((group) => (
          <GroupComponent key={group.groupLetter} group={group} />
        ))}
      </div>

      {/* Third Row: Groups I-L */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {thirdRowGroups.map((group) => (
          <GroupComponent key={group.groupLetter} group={group} />
        ))}
      </div>
    </div>
  )
}

