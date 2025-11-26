import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

export const NavBar: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-neutral-DEFAULT/20 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-primary-medium rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">P</span>
              </div>
            </div>
            <span className="ml-3 text-xl font-bold text-neutral-DEFAULT">Predico</span>
          </div>

          {/* User Menu */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-neutral-light transition-colors"
            >
              {/* Football/User Icon */}
              <div className="w-8 h-8 bg-primary-medium rounded-full flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <span className="text-neutral-DEFAULT font-medium">{user?.username || 'User'}</span>
              <svg
                className={`w-4 h-4 text-neutral-DEFAULT transition-transform ${
                  isMenuOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-neutral-DEFAULT/20 z-50">
                <div className="py-1">
                  <button
                    onClick={() => {
                      setIsMenuOpen(false)
                      // TODO: Navigate to edit profile page
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light transition-colors"
                  >
                    Edit Profile
                  </button>
                  <button
                    onClick={() => {
                      setIsMenuOpen(false)
                      // TODO: Navigate to account settings page
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light transition-colors"
                  >
                    Account Settings
                  </button>
                  <div className="border-t border-neutral-DEFAULT/20 my-1"></div>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-neutral-light transition-colors"
                  >
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}


