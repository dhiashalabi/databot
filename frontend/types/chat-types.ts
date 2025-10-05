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
  feedback?: MessageFeedback
}

export interface MessageFeedback {
  id: string
  rating: "positive" | "negative"
  comment?: string
  created_at: Date
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
}

export interface FeedbackRequest {
  chat_history_id?: string
  rating: 1 | 2 | 3 | 4 | 5
  feedback_text?: string
  category?: string
  is_helpful?: boolean
}
