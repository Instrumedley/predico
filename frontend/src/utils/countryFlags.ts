/**
 * Utility for mapping ISO 3166-1 alpha-3 country codes to ISO 3166-1 alpha-2 codes
 * for use with the flag-icons library.
 * 
 * flag-icons uses 2-letter ISO codes (alpha-2), but our database uses 3-letter codes (alpha-3).
 */

/**
 * Maps ISO 3166-1 alpha-3 country codes to alpha-2 codes for flag-icons
 */
export const COUNTRY_CODE_MAP: Record<string, string> = {
  // A
  'ARG': 'ar', // Argentina
  'AUS': 'au', // Australia
  'AUT': 'at', // Austria
  'ALB': 'al', // Albania
  'DZA': 'dz', // Algeria
  // B
  'BEL': 'be', // Belgium
  'BRA': 'br', // Brazil
  // C
  'CAN': 'ca', // Canada
  'CHI': 'cl', // Chile
  'CHN': 'cn', // China
  'COL': 'co', // Colombia
  'CRC': 'cr', // Costa Rica
  'HRV': 'hr', // Croatia
  'CUB': 'cu', // Cuba
  'CUW': 'cw', // Curaçao
  'CPV': 'cv', // Cape Verde
  'CZE': 'cz', // Czech Republic
  'CMR': 'cm', // Cameroon
  'COD': 'cd', // DR Congo
  // D
  'DEN': 'dk', // Denmark
  'DEU': 'de', // Germany
  // E
  'ECU': 'ec', // Ecuador
  'EGY': 'eg', // Egypt
  'ENG': 'gb-eng', // England (flag-icons uses gb-eng for England)
  'ESP': 'es', // Spain
  // F
  'FIN': 'fi', // Finland
  'FRA': 'fr', // France
  // G
  'GHA': 'gh', // Ghana
  // H
  'HTI': 'ht', // Haiti
  'HUN': 'hu', // Hungary
  // I
  'IRL': 'ie', // Ireland
  'IRN': 'ir', // Iran
  'IRQ': 'iq', // Iraq
  'ISR': 'il', // Israel
  'ITA': 'it', // Italy
  'CIV': 'ci', // Ivory Coast
  // J
  'JPN': 'jp', // Japan
  'JOR': 'jo', // Jordan
  // K
  'KOR': 'kr', // South Korea
  // M
  'MAR': 'ma', // Morocco
  'MEX': 'mx', // Mexico
  // N
  'NED': 'nl', // Netherlands
  'NGA': 'ng', // Nigeria
  'NOR': 'no', // Norway
  'NZL': 'nz', // New Zealand
  // P
  'PAN': 'pa', // Panama
  'PAR': 'py', // Paraguay
  'PER': 'pe', // Peru
  'POL': 'pl', // Poland
  'PRT': 'pt', // Portugal
  // Q
  'QAT': 'qa', // Qatar
  // R
  'ROU': 'ro', // Romania
  'RUS': 'ru', // Russia
  // S
  'SAU': 'sa', // Saudi Arabia
  'SCO': 'gb-sct', // Scotland (flag-icons uses gb-sct for Scotland)
  'SEN': 'sn', // Senegal
  'SWE': 'se', // Sweden
  'CHE': 'ch', // Switzerland
  // T
  'TUN': 'tn', // Tunisia
  'TUR': 'tr', // Turkey
  // U
  'UAE': 'ae', // United Arab Emirates
  'UKR': 'ua', // Ukraine
  'URY': 'uy', // Uruguay
  'USA': 'us', // United States
  'UZB': 'uz', // Uzbekistan
  // V
  'VEN': 've', // Venezuela
  // Z
  'ZAF': 'za', // South Africa
}

/**
 * Converts an ISO 3166-1 alpha-3 country code to alpha-2 code for flag-icons
 * @param code - 3-letter country code (e.g., 'USA', 'BRA')
 * @returns 2-letter country code for flag-icons (e.g., 'us', 'br')
 */
export function getCountryCodeForFlag(code: string): string {
  // If it's already a 2-letter code, return it as-is
  if (code.length === 2) {
    return code.toLowerCase()
  }
  
  // Look up in the map
  const mapped = COUNTRY_CODE_MAP[code.toUpperCase()]
  if (mapped) {
    return mapped
  }
  
  // Fallback: try to use first 2 letters (not always accurate but better than nothing)
  return code.toLowerCase().slice(0, 2)
}

