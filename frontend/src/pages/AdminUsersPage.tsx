import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { NavBar } from '@/components/layout/NavBar'
import { AdminSubNav } from '@/components/admin/AdminSubNav'
import {
  AdminUserSort,
  getAdminUserPredictions,
  listAdminUsers,
} from '@/services/admin'
import { getCountryCodeForFlag } from '@/utils/countryFlags'

function formatScoreLabel(status: string, points: number): string {
  if (status !== 'finished') {
    return 'Not computed'
  }
  return String(points)
}

export const AdminUsersPage: React.FC = () => {
  const [searchInput, setSearchInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [sort, setSort] = useState<AdminUserSort>('username')
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchQuery(searchInput.trim())
    }, 300)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['adminUsers', searchQuery, sort],
    queryFn: () => listAdminUsers(searchQuery || undefined, sort),
  })

  const { data: predictionsData, isLoading: predictionsLoading } = useQuery({
    queryKey: ['adminUserPredictions', selectedUserId],
    queryFn: () => getAdminUserPredictions(selectedUserId!),
    enabled: selectedUserId !== null,
  })

  const users = usersData?.users ?? []

  return (
    <div className="min-h-screen bg-neutral-light">
      <NavBar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-neutral-DEFAULT">Admin Panel</h1>
          <p className="text-sm text-neutral-DEFAULT/70 mt-2">
            Browse users and review their predictions
          </p>
        </div>

        <AdminSubNav />

        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
          <div className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-4">
            <div className="space-y-4 mb-4">
              <div>
                <label
                  htmlFor="user-search"
                  className="block text-sm font-medium text-neutral-DEFAULT mb-1"
                >
                  Search username or email
                </label>
                <input
                  id="user-search"
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search..."
                  className="w-full px-3 py-2 border border-neutral-DEFAULT/20 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-medium"
                />
              </div>
              <div>
                <label
                  htmlFor="user-sort"
                  className="block text-sm font-medium text-neutral-DEFAULT mb-1"
                >
                  Sort by
                </label>
                <select
                  id="user-sort"
                  value={sort}
                  onChange={(e) => setSort(e.target.value as AdminUserSort)}
                  className="w-full px-3 py-2 border border-neutral-DEFAULT/20 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-medium bg-white"
                >
                  <option value="username">Alphabetical (username)</option>
                  <option value="created_at">Date created (newest first)</option>
                </select>
              </div>
            </div>

            {usersLoading ? (
              <p className="text-sm text-neutral-DEFAULT/70">Loading users...</p>
            ) : users.length === 0 ? (
              <p className="text-sm text-neutral-DEFAULT/70">No users found.</p>
            ) : (
              <div className="max-h-[520px] overflow-y-auto border border-neutral-DEFAULT/10 rounded-md">
                <ul className="divide-y divide-neutral-DEFAULT/10">
                  {users.map((user) => {
                    const isSelected = selectedUserId === user.id
                    return (
                      <li key={user.id}>
                        <button
                          type="button"
                          onClick={() => setSelectedUserId(user.id)}
                          className={`w-full text-left px-3 py-3 transition-colors ${
                            isSelected
                              ? 'bg-primary-medium/10 border-l-4 border-primary-medium'
                              : 'hover:bg-neutral-light'
                          }`}
                        >
                          <div className="font-medium text-neutral-DEFAULT">{user.username}</div>
                          <div className="text-xs text-neutral-DEFAULT/60 mt-1">
                            {new Date(user.created_at).toLocaleDateString()} · {user.total_points} pts
                          </div>
                        </button>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}

            {usersData && (
              <p className="text-xs text-neutral-DEFAULT/60 mt-3">
                Showing {users.length} of {usersData.total} users
              </p>
            )}
          </div>

          <div className="bg-white rounded-lg border border-neutral-DEFAULT/20 shadow-sm p-6">
            {!selectedUserId ? (
              <p className="text-neutral-DEFAULT/70">
                Select a user from the list to view their predictions.
              </p>
            ) : predictionsLoading ? (
              <p className="text-neutral-DEFAULT/70">Loading predictions...</p>
            ) : !predictionsData ? (
              <p className="text-neutral-DEFAULT/70">Unable to load predictions.</p>
            ) : (
              <>
                <div className="mb-6">
                  <h2 className="text-xl font-bold text-neutral-DEFAULT">
                    {predictionsData.user.username}
                  </h2>
                  <p className="text-sm text-neutral-DEFAULT/70 mt-1">
                    {predictionsData.user.email} · Total score: {predictionsData.total_points} pts
                  </p>
                </div>

                {predictionsData.predictions.length === 0 ? (
                  <p className="text-neutral-DEFAULT/70">This user has no predictions yet.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-neutral-DEFAULT/20 text-left text-neutral-DEFAULT/70">
                          <th className="py-2 pr-4 font-medium">Match & prediction</th>
                          <th className="py-2 font-medium w-32">Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {predictionsData.predictions.map((prediction) => {
                          const { game } = prediction
                          const scoreLabel = formatScoreLabel(game.status, prediction.points)

                          return (
                            <tr
                              key={prediction.id}
                              className="border-b border-neutral-DEFAULT/10 last:border-0"
                            >
                              <td className="py-3 pr-4">
                                <div className="flex flex-wrap items-center gap-2 text-neutral-DEFAULT">
                                  <span
                                    className={`fi fi-${getCountryCodeForFlag(game.home_team.country_code)} fis`}
                                    style={{ fontSize: '1.1rem' }}
                                  />
                                  <span className="font-medium">{game.home_team.name}</span>
                                  <span className="px-2 py-0.5 rounded bg-neutral-light font-semibold">
                                    {prediction.predicted_home_score}
                                  </span>
                                  <span className="text-neutral-DEFAULT/60">vs</span>
                                  <span className="px-2 py-0.5 rounded bg-neutral-light font-semibold">
                                    {prediction.predicted_away_score}
                                  </span>
                                  <span className="font-medium">{game.away_team.name}</span>
                                  <span
                                    className={`fi fi-${getCountryCodeForFlag(game.away_team.country_code)} fis`}
                                    style={{ fontSize: '1.1rem' }}
                                  />
                                </div>
                              </td>
                              <td className="py-3">
                                <span
                                  className={
                                    scoreLabel === 'Not computed'
                                      ? 'text-neutral-DEFAULT/60 italic'
                                      : 'font-semibold text-neutral-DEFAULT'
                                  }
                                >
                                  {scoreLabel}
                                </span>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
