/**
 * Timezone utility functions for handling match times and deadlines
 */
import { Match } from '@/types/matches'

/**
 * Parse timezone string like "UTC-5" or "UTC+3" to offset in hours.
 * Returns offset in hours (e.g., -5 for UTC-5, +3 for UTC+3).
 */
export function parseTimezoneOffset(timezoneStr: string): number {
  if (!timezoneStr) {
    return 0
  }

  const match = timezoneStr.trim().match(/UTC([+-]?\d+)/i)
  if (match) {
    return parseInt(match[1], 10)
  }
  return 0
}

/**
 * Ensure API datetimes without an explicit offset are treated as UTC.
 */
export function parseUtcDateTime(isoString: string): Date {
  if (!isoString) {
    return new Date(NaN)
  }
  if (/[zZ]$/.test(isoString) || /[+-]\d{2}:\d{2}$/.test(isoString)) {
    return new Date(isoString)
  }
  return new Date(`${isoString}Z`)
}

/**
 * Convert match date, time, and timezone to UTC Date object.
 * Returns null if matchDate, matchTime, or timezone is missing.
 */
export function getMatchDatetimeUTC(
  matchDate: string,
  matchTime: string,
  timezone: string
): Date | null {
  if (!matchDate || !matchTime || !timezone) {
    return null
  }

  const tzOffsetHours = parseTimezoneOffset(timezone)
  const [year, month, day] = matchDate.split('-').map(Number)
  const [hours, minutes, seconds = 0] = matchTime.split(':').map(Number)

  const utcDate = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds))
  return new Date(utcDate.getTime() - tzOffsetHours * 60 * 60 * 1000)
}

/**
 * Canonical kickoff instant for a match (UTC).
 */
export function getMatchKickoffUTC(match: Pick<Match, 'scheduledAt' | 'matchDate' | 'matchTime' | 'timezone'>): Date | null {
  if (match.scheduledAt) {
    return parseUtcDateTime(match.scheduledAt)
  }

  if (match.matchDate && match.matchTime && match.timezone) {
    return getMatchDatetimeUTC(match.matchDate, match.matchTime, match.timezone)
  }

  return null
}

/**
 * Calculate deadline datetime (1 hour before match start).
 * Returns the deadline as a Date object in UTC.
 */
export function calculateDeadline(
  matchDate: string | undefined,
  matchTime: string | undefined,
  timezone: string | undefined
): Date | null {
  if (!matchDate || !matchTime || !timezone) {
    return null
  }

  const matchDatetime = getMatchDatetimeUTC(matchDate, matchTime, timezone)
  if (!matchDatetime) {
    return null
  }

  return new Date(matchDatetime.getTime() - 60 * 60 * 1000)
}

/**
 * Calculate deadline from a match object.
 */
export function getPredictionDeadline(match: Pick<Match, 'scheduledAt' | 'matchDate' | 'matchTime' | 'timezone' | 'status'>): Date | null {
  if (match.status !== 'scheduled') {
    return null
  }

  const kickoff = getMatchKickoffUTC(match)
  if (!kickoff) {
    return null
  }

  return new Date(kickoff.getTime() - 60 * 60 * 1000)
}

/**
 * True when predictions should be locked (1 hour before kickoff or non-scheduled).
 */
export function isPredictionLocked(
  match: Pick<Match, 'scheduledAt' | 'matchDate' | 'matchTime' | 'timezone' | 'status'>,
  now: Date = new Date()
): boolean {
  if (match.status !== 'scheduled') {
    return true
  }

  const deadline = getPredictionDeadline(match)
  if (!deadline) {
    return false
  }

  return now.getTime() >= deadline.getTime()
}

/**
 * Format kickoff in the user's local timezone.
 */
export function formatMatchKickoffLocal(
  match: Pick<Match, 'scheduledAt' | 'matchDate' | 'matchTime' | 'timezone'>,
  options?: Intl.DateTimeFormatOptions
): { date: string; time: string } | null {
  const kickoff = getMatchKickoffUTC(match)
  if (!kickoff || Number.isNaN(kickoff.getTime())) {
    return null
  }

  const defaultOptions: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }

  const formatter = new Intl.DateTimeFormat(undefined, options ?? defaultOptions)
  const parts = formatter.formatToParts(kickoff)

  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.filter((part) => part.type === type).map((part) => part.value).join('')

  const date = `${get('weekday')} ${get('month')} ${get('day')}`.trim()
  const time = `${get('hour')}:${get('minute')} ${get('dayPeriod')}`.trim()

  return { date, time }
}

/**
 * Format date only in the user's local timezone.
 */
export function formatMatchDateLocal(isoString: string): string {
  const date = parseUtcDateTime(isoString)
  return date.toLocaleDateString(undefined, {
    month: 'long',
    day: 'numeric',
  })
}
