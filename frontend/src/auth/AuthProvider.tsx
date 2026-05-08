import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from 'react'
import {
  clearApiAccessToken,
  getCurrentUser,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
  setApiAccessToken,
  socialLogin as socialLoginApi,
} from '../services/api'
import { type AuthUser, type LoginPayload, type RegisterPayload, type SocialLoginPayload } from '../types'

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  socialLogin: (payload: SocialLoginPayload) => Promise<void>
  logout: () => Promise<void>
}

interface StoredSession {
  accessToken: string
  user: AuthUser
}

const AUTH_STORAGE_KEY = 'mediwatch.auth.session'

const AuthContext = createContext<AuthContextValue | null>(null)

const readStoredSession = (): StoredSession | null => {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw) as StoredSession
    if (!parsed.accessToken || !parsed.user) {
      return null
    }
    return parsed
  } catch {
    return null
  }
}

const storeSession = (session: StoredSession): void => {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
}

const clearStoredSession = (): void => {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

export const AuthProvider = ({ children }: { children: ReactNode }): JSX.Element => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const bootstrapSession = async (): Promise<void> => {
      const session = readStoredSession()
      if (!session) {
        clearApiAccessToken()
        setIsLoading(false)
        return
      }

      setApiAccessToken(session.accessToken)
      try {
        const currentUser = await getCurrentUser()
        setUser(currentUser)
        storeSession({ accessToken: session.accessToken, user: currentUser })
      } catch {
        clearApiAccessToken()
        clearStoredSession()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    void bootstrapSession()
  }, [])

  const login = async (payload: LoginPayload): Promise<void> => {
    const response = await loginApi(payload)
    setApiAccessToken(response.access_token)
    setUser(response.user)
    storeSession({ accessToken: response.access_token, user: response.user })
  }

  const register = async (payload: RegisterPayload): Promise<void> => {
    await registerApi(payload)
    const response = await loginApi({ username: payload.username, password: payload.password })
    setApiAccessToken(response.access_token)
    setUser(response.user)
    storeSession({ accessToken: response.access_token, user: response.user })
  }

  const socialLogin = async (payload: SocialLoginPayload): Promise<void> => {
    const response = await socialLoginApi(payload)
    setApiAccessToken(response.access_token)
    setUser(response.user)
    storeSession({ accessToken: response.access_token, user: response.user })
  }

  const logout = async (): Promise<void> => {
    await logoutApi()
    clearApiAccessToken()
    clearStoredSession()
    setUser(null)
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      socialLogin,
      logout,
    }),
    [user, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
