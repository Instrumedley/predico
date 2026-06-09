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
