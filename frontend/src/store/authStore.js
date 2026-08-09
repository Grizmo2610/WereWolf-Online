import { create } from 'zustand'
import { api } from '../api/client'

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  hydrate: async () => {
    try {
      const user = await api.me()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  login: async (username, password) => {
    const res = await api.login(username, password)
    set({ user: res.user, isAuthenticated: true })
  },

  register: async (username, password, displayName) => {
    const res = await api.register(username, password, displayName)
    set({ user: res.user, isAuthenticated: true })
  },

  logout: async () => {
    await api.logout()
    set({ user: null, isAuthenticated: false })
  },
}))
