import React, { useState } from 'react'
import { NavBar, MiniMenu, DeadlineCard } from '@/components/layout'
import { GroupStandingsComponent } from '@/components/standings'

type MenuOption = 'dashboard' | 'scorecard' | 'leagues'

export const DashboardPage: React.FC = () => {
  const [activeMenuOption, setActiveMenuOption] = useState<MenuOption>('dashboard')

  return (
    <div className="min-h-screen bg-neutral-light">
      {/* NavBar */}
      <NavBar />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Mini Menu */}
        <MiniMenu activeOption={activeMenuOption} onOptionChange={setActiveMenuOption} />

        {/* Deadline Card */}
        <DeadlineCard roundNumber={13} />

        {/* Group Stage Standings */}
        <div className="mt-8">
          <GroupStandingsComponent />
        </div>

        {/* Placeholder for future components */}
        <div className="mt-8">
          {/* NextMatch, LatestResults will go here */}
        </div>
      </div>
    </div>
  )
}


