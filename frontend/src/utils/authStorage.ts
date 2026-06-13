const ACCESS_TOKEN_KEY = 'access_token'
const USER_DATA_KEY = 'user_data'
const REMEMBER_ME_KEY = 'remember_me'

function getPersistentStorage(rememberMe: boolean): Storage {
  return rememberMe ? localStorage : sessionStorage
}

export function getRememberMePreference(): boolean {
  return localStorage.getItem(REMEMBER_ME_KEY) === 'true'
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY) ?? sessionStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getUserDataRaw(): string | null {
  return localStorage.getItem(USER_DATA_KEY) ?? sessionStorage.getItem(USER_DATA_KEY)
}

export function setAuthSession(
  accessToken: string,
  userData: object,
  rememberMe: boolean
): void {
  clearAuthSession()
  const storage = getPersistentStorage(rememberMe)
  storage.setItem(ACCESS_TOKEN_KEY, accessToken)
  storage.setItem(USER_DATA_KEY, JSON.stringify(userData))
  if (rememberMe) {
    localStorage.setItem(REMEMBER_ME_KEY, 'true')
  } else {
    localStorage.removeItem(REMEMBER_ME_KEY)
  }
}

export function updateStoredUserData(userData: object): void {
  if (!getAccessToken()) {
    return
  }

  const storage = getRememberMePreference() ? localStorage : sessionStorage
  storage.setItem(USER_DATA_KEY, JSON.stringify(userData))
}

export function clearAuthSession(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(USER_DATA_KEY)
  localStorage.removeItem(REMEMBER_ME_KEY)
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
  sessionStorage.removeItem(USER_DATA_KEY)
}
