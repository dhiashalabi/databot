import type { EnhancedError } from "./error-types"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  data?: unknown
  error?: EnhancedError | unknown
  isTyping?: boolean
  chat_history_id?: string
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
  chat_history_id: string
  feedback_type: "thumbs_up" | "thumbs_down" | "rating" | "detailed"
  rating?: 1 | 2 | 3 | 4 | 5
  is_liked?: boolean
  feedback_text?: string
  helpfulness_rating?: 1 | 2 | 3 | 4 | 5
  accuracy_rating?: 1 | 2 | 3 | 4 | 5
  relevance_rating?: 1 | 2 | 3 | 4 | 5
  suggested_improvements?: string
  reported_issues?: string
}
