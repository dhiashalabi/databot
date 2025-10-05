import type { EnhancedError } from "./error-types"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  data?: unknown
  error?: EnhancedError | unknown
  isTyping?: boolean
  files?: Array<{
    url: string
    filename: string
    type?: string
    success?: boolean
    message?: string
    record_count?: number
    sheets?: string[]
  }>
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
}
