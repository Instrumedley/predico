import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { NavBar, MiniMenu, DeadlineCard } from '@/components/layout'
import { GroupStandingsComponent } from '@/components/standings'
import { NextMatch, LatestResults } from '@/components/matches'

type MenuOption = 'dashboard' | 'scorecard' | 'leagues'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [activeMenuOption, setActiveMenuOption] = useState<MenuOption>('dashboard')

  const handleMenuOptionChange = (option: MenuOption) => {
    setActiveMenuOption(option)
    if (option === 'scorecard') {
      navigate('/scorecard')
    }
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      {/* NavBar */}
      <NavBar />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Mini Menu */}
        <MiniMenu activeOption={activeMenuOption} onOptionChange={handleMenuOptionChange} />

        {/* Deadline Card */}
        <DeadlineCard roundNumber={13} />

        {/* Group Stage Standings */}
        <div className="mt-8">
          <GroupStandingsComponent />
        </div>

        {/* Next Match and Latest Results */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Next Match */}
          <div>
            <NextMatch />
          </div>

          {/* Latest Results */}
          <div>
            <LatestResults />
          </div>
        </div>
      </div>
    </div>
  )
}


