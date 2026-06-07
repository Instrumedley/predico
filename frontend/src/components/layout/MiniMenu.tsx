import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getMyLeagues } from '@/services/leagues'

type MenuOption = 'dashboard' | 'scorecard' | 'leagues'

interface MiniMenuProps {
  activeOption?: MenuOption
  onOptionChange?: (option: MenuOption) => void
}

export const MiniMenu: React.FC<MiniMenuProps> = ({ activeOption = 'dashboard', onOptionChange }) => {
  const navigate = useNavigate()
  const [isLeaguesMenuOpen, setIsLeaguesMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const { data: leagues = [], isLoading } = useQuery({
    queryKey: ['myLeagues'],
    queryFn: getMyLeagues,
    staleTime: 30 * 1000,
  })

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
    navigate('/leagues/create')
  }

  const handleGlobalLeagues = () => {
    setIsLeaguesMenuOpen(false)
    navigate('/leagues/browse')
  }

  return (
    <div className="flex justify-center py-4">
      <div className="flex items-center space-x-1 bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm px-2">
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
              className={`w-4 h-4 transition-transform ${isLeaguesMenuOpen ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {isLeaguesMenuOpen && (
            <div className="absolute left-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-neutral-DEFAULT/20 z-50">
              <div className="py-1 max-h-64 overflow-y-auto">
                {isLoading ? (
                  <div className="px-4 py-2 text-sm text-neutral-DEFAULT/60">Loading...</div>
                ) : leagues.length === 0 ? (
                  <div className="px-4 py-2 text-sm text-neutral-DEFAULT/60">No leagues yet</div>
                ) : (
                  leagues.map((league) => (
                    <button
                      key={league.id}
                      onClick={() => {
                        setIsLeaguesMenuOpen(false)
                        navigate(`/leagues/${league.id}`)
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light transition-colors"
                    >
                      <span className="inline-flex items-center gap-2">
                        {league.name}
                        {league.is_private && (
                          <svg className="w-3.5 h-3.5 text-neutral-DEFAULT/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                        )}
                      </span>
                    </button>
                  ))
                )}

                <div className="border-t border-neutral-DEFAULT/20 my-1" />

                <button
                  onClick={handleCreateLeague}
                  className="block w-full text-left px-4 py-2 text-sm text-primary-medium hover:bg-neutral-light transition-colors font-medium"
                >
                  + Create new league
                </button>

                <button
                  onClick={handleGlobalLeagues}
                  className="block w-full text-left px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light transition-colors"
                >
                  <span className="inline-flex items-center gap-2">
                    <svg className="w-4 h-4 text-primary-medium" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Global leagues
                  </span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
