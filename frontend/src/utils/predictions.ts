export const PREDICTION_MAX_POINTS = 100

export interface PredictionRowColors {
  backgroundColor: string
  color: string
}

export function formatPredictionScoreLabel(status: string, points: number): string {
  if (status !== 'finished') {
    return 'Not computed'
  }
  return String(points)
}

export function formatMatchDateLabel(matchDate?: string | null, scheduledAt?: string): string {
  const value = matchDate || scheduledAt
  if (!value) {
    return '—'
  }
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Row/card colors for finalized predictions — matches scorecard styling.
 */
export function getPredictionRowColors(
  status: string,
  points: number,
  hasPrediction = true
): PredictionRowColors {
  if (!hasPrediction || status !== 'finished') {
    return { backgroundColor: 'white', color: 'inherit' }
  }

  if (points === PREDICTION_MAX_POINTS) {
    return { backgroundColor: 'lightgreen', color: 'darkgreen' }
  }

  if (points === 0) {
    return { backgroundColor: '#d1d5db', color: '#374151' }
  }

  return { backgroundColor: '#FF9869', color: 'navajowhite' }
}
