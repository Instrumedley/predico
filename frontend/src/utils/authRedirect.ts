const AUTH_REDIRECT_KEY = 'predico_auth_redirect'

export function saveAuthRedirect(path: string): void {
  sessionStorage.setItem(AUTH_REDIRECT_KEY, path)
}

export function getAuthRedirect(): string | null {
  return sessionStorage.getItem(AUTH_REDIRECT_KEY)
}

export function consumeAuthRedirect(fallback = '/dashboard'): string {
  const stored = sessionStorage.getItem(AUTH_REDIRECT_KEY)
  if (stored) {
    sessionStorage.removeItem(AUTH_REDIRECT_KEY)
    return stored
  }
  return fallback
}

export function buildLoginPath(redirectPath?: string | null): string {
  if (!redirectPath) {
    return '/login'
  }
  return `/login?redirect=${encodeURIComponent(redirectPath)}`
}

export function buildSignupPath(redirectPath?: string | null): string {
  if (!redirectPath) {
    return '/signup'
  }
  return `/signup?redirect=${encodeURIComponent(redirectPath)}`
}
