import { create } from "zustand"

interface UIState {
  input: string
  setInput: (input: string) => void
  clearInput: () => void

  copiedId: string | null
  setCopiedId: (id: string | null) => void

  isErrorExpanded: boolean
  setIsErrorExpanded: (expanded: boolean) => void

  isThemeMounted: boolean
  setIsThemeMounted: (mounted: boolean) => void

  isMobile: boolean | undefined
  setIsMobile: (mobile: boolean | undefined) => void

  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void

  reset: () => void
}

const initialState = {
  input: "",
  copiedId: null,
  isErrorExpanded: false,
  isThemeMounted: false,
  isMobile: undefined,
  sidebarOpen: false,
}

export const useUIStore = create<UIState>(set => ({
  ...initialState,

  setInput: (input: string) => set({ input }),
  clearInput: () => set({ input: "" }),

  setCopiedId: (id: string | null) => set({ copiedId: id }),

  setIsErrorExpanded: (expanded: boolean) => set({ isErrorExpanded: expanded }),

  setIsThemeMounted: (mounted: boolean) => set({ isThemeMounted: mounted }),

  setIsMobile: (mobile: boolean | undefined) => set({ isMobile: mobile }),

  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

  reset: () => set(initialState),
}))
