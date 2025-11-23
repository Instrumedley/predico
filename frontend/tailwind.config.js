/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#C3F73A', // Bright green/yellow
          light: '#95E06C',  // Light green
          medium: '#68B684',  // Medium green
          dark: '#68B684',    // Medium green (darker variant)
        },
        neutral: {
          DEFAULT: '#7A7D7D', // Gray
          light: '#FFFBFE',    // Off-white/cream
        },
        accent: {
          bright: '#C3F73A',
          light: '#95E06C',
          medium: '#68B684',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

