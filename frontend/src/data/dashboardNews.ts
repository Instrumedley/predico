export interface DashboardNewsItem {
  id: string
  message: string
  link?: {
    href: string
    label: string
  }
}

/** Active dashboard announcements shown when DASHBOARD_NEWS_BANNER_ENABLED is on. */
export const DASHBOARD_NEWS_ITEMS: DashboardNewsItem[] = [
  {
    id: 'league-tie-breaker-2026-05',
    message:
      'League rankings now use perfect predictions as a tie-breaker when two players have the same total score.',
    link: {
      href: '/faq',
      label: 'See the FAQ for this update and the full scoring system',
    },
  },
]
