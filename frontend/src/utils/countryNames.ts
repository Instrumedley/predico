/**
 * Utility functions for country name formatting
 * Abbreviates long country names to fit in table cells
 */

const countryAbbreviations: Record<string, string> = {
  'United States': 'USA',
  'United Arab Emirates': 'UAE',
  'New Zealand': 'N. Zealand',
  'Czech Republic': 'Czechia',
  'South Korea': 'S. Korea',
  'Saudi Arabia': 'Saudi Arabia', // Already short enough
  'Costa Rica': 'Costa Rica', // Already short enough
}

/**
 * Abbreviates country name if it's longer than 12 characters or has a known abbreviation
 * @param countryName - Full country name
 * @returns Abbreviated country name (max 12 characters)
 */
export const abbreviateCountryName = (countryName: string): string => {
  // Check if there's a specific abbreviation
  if (countryAbbreviations[countryName]) {
    return countryAbbreviations[countryName]
  }

  // If name is 12 characters or less, return as is
  if (countryName.length <= 12) {
    return countryName
  }

  // Truncate to 12 characters
  return countryName.substring(0, 12)
}

