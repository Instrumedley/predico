import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { NavBar, MiniMenu, DeadlineCard, type MenuOption } from '@/components/layout'
import { GroupStandingsComponent } from '@/components/standings'
import { NextMatch, LatestResults } from '@/components/matches'
import { DashboardStageTabs, KnockoutBracket, type DashboardStage } from '@/components/knockout'
import { getFeatureFlags } from '@/services/config'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [activeMenuOption, setActiveMenuOption] = useState<MenuOption>('dashboard')
  const [activeStage, setActiveStage] = useState<DashboardStage>('group')
  const defaultStageApplied = useRef(false)

  const { data: featureFlags } = useQuery({
    queryKey: ['featureFlags'],
    queryFn: getFeatureFlags,
    staleTime: 60_000,
  })

  const knockoutStageEnabled = featureFlags?.knockout_stage ?? false

  useEffect(() => {
    if (defaultStageApplied.current || !featureFlags?.knockout_stage) {
      return
    }

    setActiveStage(featureFlags.knockout_stage_default ? 'knockout' : 'group')
    defaultStageApplied.current = true
  }, [featureFlags])

  const handleMenuOptionChange = (option: MenuOption) => {
    setActiveMenuOption(option)
    if (option === 'scorecard') {
      navigate('/scorecard')
    } else if (option === 'dashboard') {
      navigate('/dashboard')
    }
  }

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <MiniMenu activeOption={activeMenuOption} onOptionChange={handleMenuOptionChange} />

        <DeadlineCard />

        <div className="mt-8">
          {knockoutStageEnabled && (
            <div className="mb-5">
              <DashboardStageTabs activeStage={activeStage} onStageChange={setActiveStage} />
            </div>
          )}

          {activeStage === 'knockout' && knockoutStageEnabled ? (
            <KnockoutBracket />
          ) : (
            <GroupStandingsComponent />
          )}
        </div>

        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <NextMatch />
          </div>
          <div>
            <LatestResults />
          </div>
        </div>
      </div>
    </div>
  )
}
