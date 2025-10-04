export interface ValidationError {
  type: "validation_error"
  message: string
  validation_errors: string[]
  suggestions?: string[]
}

export interface BackendError {
  type: "backend_error"
  message: string
  code?: string
  details?: Record<string, unknown>
}

export interface NetworkError {
  type: "network_error"
  message: string
  status?: number
  statusText?: string
}

export interface UnknownError {
  type: "unknown_error"
  message: string
  originalError?: unknown
}

export type AppError = ValidationError | BackendError | NetworkError | UnknownError

export type ErrorSeverity = "low" | "medium" | "high" | "critical"

export type ErrorCategory =
  | "validation"
  | "security"
  | "network"
  | "server"
  | "database"
  | "authentication"
  | "authorization"
  | "rate_limit"
  | "unknown"

export type EnhancedError = AppError & {
  severity: ErrorSeverity
  category: ErrorCategory
  timestamp: Date
  userMessage: string
  technicalMessage: string
  canRetry: boolean
  retryAfter?: number
  suggestions?: string[]
  helpUrl?: string
}
