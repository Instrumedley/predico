/**
 * Timezone utility functions for handling match times and deadlines
 */

/**
 * Parse timezone string like "UTC-5" or "UTC+3" to offset in hours.
 * Returns offset in hours (e.g., -5 for UTC-5, +3 for UTC+3).
 */
export function parseTimezoneOffset(timezoneStr: string): number {
  if (!timezoneStr) {
    return 0
  }

  // Remove "UTC" prefix and parse the offset
  const match = timezoneStr.trim().match(/UTC([+-]?\d+)/i)
  if (match) {
    return parseInt(match[1], 10)
  }
  return 0
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

  // Parse timezone offset
  const tzOffsetHours = parseTimezoneOffset(timezone)

  // Parse date and time
  const [year, month, day] = matchDate.split('-').map(Number)
  const [hours, minutes, seconds = 0] = matchTime.split(':').map(Number)

  // Create date in UTC using UTC methods
  // The match time is in the local timezone (e.g., UTC-5)
  // To convert to UTC, we add the offset (if UTC-5, we add 5 hours)
  // Note: tzOffsetHours is negative for timezones behind UTC (e.g., -5 for UTC-5)
  // So we subtract it (which adds hours)
  const utcDate = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds))
  // Adjust for timezone offset: if UTC-5, we need to add 5 hours to get UTC
  const adjustedUtcDate = new Date(utcDate.getTime() - tzOffsetHours * 60 * 60 * 1000)

  return adjustedUtcDate
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

  // Subtract 1 hour for the deadline
  const deadline = new Date(matchDatetime.getTime() - 60 * 60 * 1000)
  return deadline
}
