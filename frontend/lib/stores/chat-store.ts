import { create } from "zustand"

import type { Message } from "@/types"

interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
  selectedModel: string
}

interface ChatActions {
  addMessage: (message: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSelectedModel: (model: string) => void
  clearMessages: () => void
  reset: () => void
}

type ChatStore = ChatState & ChatActions

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
  selectedModel: "",
}

export const useChatStore = create<ChatStore>(set => ({
  ...initialState,

  addMessage: (message: Message) =>
    set(state => ({
      messages: [...state.messages, message],
    })),

  updateMessage: (id: string, updates: Partial<Message>) =>
    set(state => ({
      messages: state.messages.map(msg => (msg.id === id ? { ...msg, ...updates } : msg)),
    })),

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  setError: (error: string | null) => set({ error }),

  setSelectedModel: (model: string) => set({ selectedModel: model }),

  clearMessages: () => set({ messages: [], isLoading: false, error: null }),

  reset: () => set(initialState),
}))
