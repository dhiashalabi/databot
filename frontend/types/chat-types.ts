import type { EnhancedError } from "./error-types"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  data?: unknown
  error?: EnhancedError | unknown
  isTyping?: boolean
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
}
