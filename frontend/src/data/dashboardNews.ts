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
      'The knockout stage matches are now open for you to enter your predictions! Good luck and Go Netherlands!',
  },
]
