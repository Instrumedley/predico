import React from 'react'

export type DashboardStage = 'group' | 'knockout'

interface DashboardStageTabsProps {
  activeStage: DashboardStage
  onStageChange: (stage: DashboardStage) => void
}

export const DashboardStageTabs: React.FC<DashboardStageTabsProps> = ({
  activeStage,
  onStageChange,
}) => {
  const tabs: { id: DashboardStage; label: string }[] = [
    { id: 'group', label: 'Group Stage' },
    { id: 'knockout', label: 'Knockout Stage' },
  ]

  return (
    <div
      className="inline-flex rounded-lg border border-neutral-DEFAULT/15 bg-white p-1 shadow-sm"
      role="tablist"
      aria-label="Tournament stage"
    >
      {tabs.map((tab) => {
        const isActive = activeStage === tab.id
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onStageChange(tab.id)}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-primary-medium text-white shadow-sm'
                : 'text-neutral-DEFAULT/70 hover:bg-neutral-light hover:text-neutral-DEFAULT'
            }`}
          >
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}
