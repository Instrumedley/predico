import React, { useState, useRef, useEffect } from 'react'

type MenuOption = 'dashboard' | 'scorecard' | 'leagues'

interface MiniMenuProps {
  activeOption?: MenuOption
  onOptionChange?: (option: MenuOption) => void
}

export const MiniMenu: React.FC<MiniMenuProps> = ({ activeOption = 'dashboard', onOptionChange }) => {
  const [isLeaguesMenuOpen, setIsLeaguesMenuOpen] = useState(false)
  const [leagues] = useState<string[]>([]) // TODO: Replace with actual leagues data
  const menuRef = useRef<HTMLDivElement>(null)

  // Close leagues menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsLeaguesMenuOpen(false)
      }
    }

    if (isLeaguesMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isLeaguesMenuOpen])

  const handleOptionClick = (option: MenuOption) => {
    if (option !== 'leagues') {
      onOptionChange?.(option)
    }
  }

  const handleCreateLeague = () => {
    setIsLeaguesMenuOpen(false)
    // TODO: Navigate to create league page or open modal
    console.log('Create new league')
  }

  return (
    <div className="flex justify-center py-4">
      <div className="flex items-center space-x-1 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm px-2">
        {/* Dashboard */}
        <button
          onClick={() => handleOptionClick('dashboard')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeOption === 'dashboard'
              ? 'bg-primary-medium text-white'
              : 'text-neutral-DEFAULT hover:bg-neutral-light'
          }`}
        >
          Dashboard
        </button>

        {/* Scorecard */}
        <button
          onClick={() => handleOptionClick('scorecard')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeOption === 'scorecard'
              ? 'bg-primary-medium text-white'
              : 'text-neutral-DEFAULT hover:bg-neutral-light'
          }`}
        >
          Scorecard
        </button>

        {/* My Leagues */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setIsLeaguesMenuOpen(!isLeaguesMenuOpen)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-1 ${
              activeOption === 'leagues'
                ? 'bg-primary-medium text-white'
                : 'text-neutral-DEFAULT hover:bg-neutral-light'
            }`}
          >
            <span>My Leagues</span>
            <svg
              className={`w-4 h-4 transition-transform ${
                isLeaguesMenuOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Leagues Dropdown */}
          {isLeaguesMenuOpen && (
            <div className="absolute left-0 mt-2 w-56 bg-white rounded-md shadow-lg border border-neutral-DEFAULT/20 z-50">
              <div className="py-1 max-h-64 overflow-y-auto">
                {leagues.length === 0 ? (
                  <div className="px-4 py-2 text-sm text-neutral-DEFAULT/60">
                    No leagues yet
                  </div>
                ) : (
                  leagues.map((league, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setIsLeaguesMenuOpen(false)
                        onOptionChange?.('leagues')
                        // TODO: Load specific league
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light transition-colors"
                    >
                      {league}
                    </button>
                  ))
                )}
                <div className="border-t border-neutral-DEFAULT/20 my-1"></div>
                <button
                  onClick={handleCreateLeague}
                  className="block w-full text-left px-4 py-2 text-sm text-primary-medium hover:bg-neutral-light transition-colors font-medium"
                >
                  + Create new league
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


