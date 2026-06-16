import { LeagueProgressMatchPoint } from '@/services/leagues'

export interface LeagueProgressMatrixCell {
  backgroundColor: string
  color: string
  label: string
  showBullseye: boolean
}

const MATRIX_POINT_STYLES: Record<15 | 50 | 65 | 100, Omit<LeagueProgressMatrixCell, 'label' | 'showBullseye'>> = {
  15: { backgroundColor: '#dcfce7', color: '#166534' },
  50: { backgroundColor: '#86efac', color: '#14532d' },
  65: { backgroundColor: '#4ade80', color: '#14532d' },
  100: { backgroundColor: '#16a34a', color: '#ffffff' },
}

const WRONG_PREDICTION_STYLE = {
  backgroundColor: '#d1d5db',
  color: '#374151',
}

const NO_PREDICTION_STYLE = {
  backgroundColor: '#ffffff',
  color: '#9ca3af',
}

function resolvePointStyle(points: number): Omit<LeagueProgressMatrixCell, 'label' | 'showBullseye'> {
  if (points in MATRIX_POINT_STYLES) {
    return MATRIX_POINT_STYLES[points as 15 | 50 | 65 | 100]
  }

  if (points >= 100) {
    return MATRIX_POINT_STYLES[100]
  }
  if (points >= 65) {
    return MATRIX_POINT_STYLES[65]
  }
  if (points >= 50) {
    return MATRIX_POINT_STYLES[50]
  }
  if (points >= 15) {
    return MATRIX_POINT_STYLES[15]
  }

  return MATRIX_POINT_STYLES[15]
}

export function getLeagueProgressMatrixCell(
  matchPoint: LeagueProgressMatchPoint | undefined
): LeagueProgressMatrixCell {
  if (!matchPoint?.has_prediction) {
    return {
      ...NO_PREDICTION_STYLE,
      label: 'N/A',
      showBullseye: false,
    }
  }

  if (matchPoint.points === 0) {
    return {
      ...WRONG_PREDICTION_STYLE,
      label: '+0',
      showBullseye: false,
    }
  }

  const style = resolvePointStyle(matchPoint.points)
  return {
    ...style,
    label: `+${matchPoint.points}`,
    showBullseye: matchPoint.points === 100,
  }
}
