import { create } from 'zustand'

interface AppStore {
  activeTab: 'user' | 'moderator'
  setActiveTab: (tab: 'user' | 'moderator') => void
  loading: boolean
  setLoading: (loading: boolean) => void
  error: string | null
  setError: (error: string | null) => void
  success: string | null
  setSuccess: (success: string | null) => void
}

export const useAppStore = create<AppStore>((set) => ({
  activeTab: 'user',
  setActiveTab: (tab) => set({ activeTab: tab }),
  loading: false,
  setLoading: (loading) => set({ loading }),
  error: null,
  setError: (error) => {
    set({ error })
    if (error) setTimeout(() => set({ error: null }), 5000)
  },
  success: null,
  setSuccess: (success) => {
    set({ success })
    if (success) setTimeout(() => set({ success: null }), 5000)
  },
}))