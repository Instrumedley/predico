import React from 'react'
import { getCountryCodeForFlag } from '@/utils/countryFlags'
import {
  formatMatchDateLabel,
  formatPredictionScoreLabel,
  getPredictionRowColors,
} from '@/utils/predictions'

export interface UserPredictionRow {
  id: number
  predicted_home_score: number
  predicted_away_score: number
  points: number
  game: {
    status: string
    match_date?: string | null
    scheduled_at: string
    home_team: { name: string; country_code: string }
    away_team: { name: string; country_code: string }
  }
}

interface UserPredictionsTableProps {
  predictions: UserPredictionRow[]
  showMatchDate?: boolean
}

export const UserPredictionsTable: React.FC<UserPredictionsTableProps> = ({
  predictions,
  showMatchDate = false,
}) => {
  if (predictions.length === 0) {
    return <p className="text-sm text-neutral-DEFAULT/70">No predictions yet.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-neutral-DEFAULT/20 text-left text-neutral-DEFAULT">
            {showMatchDate && (
              <th className="py-2.5 pr-4 text-base font-bold w-32">Date</th>
            )}
            <th className="py-2.5 pr-4 text-base font-bold">Match & prediction</th>
            <th className="py-2.5 text-base font-bold w-32">Score</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction) => {
            const { game } = prediction
            const scoreLabel = formatPredictionScoreLabel(game.status, prediction.points)
            const rowColors = getPredictionRowColors(game.status, prediction.points)

            return (
              <tr
                key={prediction.id}
                style={rowColors}
              >
                {showMatchDate && (
                  <td className="py-3 pr-4 text-neutral-DEFAULT/80 whitespace-nowrap">
                    {formatMatchDateLabel(game.match_date, game.scheduled_at)}
                  </td>
                )}
                <td className="py-3 pr-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`fi fi-${getCountryCodeForFlag(game.home_team.country_code)} fis`}
                      style={{ fontSize: '1.1rem' }}
                    />
                    <span className="font-medium">{game.home_team.name}</span>
                    <span className="px-2 py-0.5 rounded bg-black/5 font-semibold">
                      {prediction.predicted_home_score}
                    </span>
                    <span className="opacity-70">vs</span>
                    <span className="px-2 py-0.5 rounded bg-black/5 font-semibold">
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
                        ? 'italic opacity-70'
                        : 'font-semibold'
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
  )
}
