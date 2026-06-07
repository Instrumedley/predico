import React, { useState } from 'react'

interface JoinLeagueModalProps {
  isOpen: boolean
  leagueName: string
  requiresPassword: boolean
  isSubmitting: boolean
  error?: string
  onClose: () => void
  onSubmit: (password?: string) => void
}

export const JoinLeagueModal: React.FC<JoinLeagueModalProps> = ({
  isOpen,
  leagueName,
  requiresPassword,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}) => {
  const [password, setPassword] = useState('')

  if (!isOpen) return null

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    onSubmit(requiresPassword ? password : undefined)
  }

  const handleClose = () => {
    setPassword('')
    onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={handleClose}
    >
      <div
        className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-neutral-DEFAULT">Join {leagueName}</h2>
        <p className="mt-2 text-sm text-neutral-DEFAULT/70">
          {requiresPassword
            ? 'Enter the league password to join this private league.'
            : 'You will join this public league and appear in its rankings.'}
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          {requiresPassword && (
            <div>
              <label htmlFor="league-password" className="block text-sm font-medium text-neutral-DEFAULT">
                League password
              </label>
              <input
                id="league-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-1 block w-full rounded-md border border-neutral-DEFAULT/30 px-3 py-2 shadow-sm focus:border-primary-medium focus:outline-none focus:ring-1 focus:ring-primary-medium"
                placeholder="Enter password"
                autoFocus
              />
            </div>
          )}

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              className="rounded-md border border-neutral-DEFAULT/20 px-4 py-2 text-sm text-neutral-DEFAULT hover:bg-neutral-light"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || (requiresPassword && !password.trim())}
              className="rounded-md bg-primary-medium px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-50"
            >
              {isSubmitting ? 'Joining...' : 'Join league'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
