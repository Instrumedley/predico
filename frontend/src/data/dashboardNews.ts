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
    id: 'knockout-predictions-open-2026-06',
    message:
      'Knockout predictions are open! Guess the full-time score after 90 minutes — extra time and penalties do not count. Good luck and Go Netherlands!',
  },
]
