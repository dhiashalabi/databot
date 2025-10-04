/**
 * Error handling utilities and formatters
 */

import type { ErrorResponse, ChatApiResponse } from "@/types/api-types"
import type { AppError, EnhancedError, ErrorSeverity } from "@/types/error-types"

export function isErrorResponse(response: ChatApiResponse): response is ErrorResponse {
  return "error" in response && response.error !== undefined
}

/**
 * Extract error from API response
 */
export function extractErrorFromResponse(response: ChatApiResponse): AppError | null {
  if (!isErrorResponse(response)) {
    return null
  }

  const { error } = response.error

  if (error.type === "validation_error") {
    return {
      type: "validation_error",
      message: error.message,
      validation_errors: error.validation_errors ?? [],
      suggestions: error.suggestions,
    }
  }

  return {
    type: "backend_error",
    message: error.message,
    code: error.code,
    details: error.details,
  }
}

/**
 * Convert various error types to EnhancedError
 */
export function enhanceError(error: unknown, _context?: string): EnhancedError {
  const timestamp = new Date()

  if (error && typeof error === "object" && "type" in error && error.type === "validation_error") {
    const validationError = error as AppError & {
      validation_errors: string[]
      suggestions?: string[]
    }
    return {
      ...validationError,
      severity: determineValidationSeverity(validationError.validation_errors),
      category: "validation",
      timestamp,
      userMessage: formatValidationUserMessage(validationError),
      technicalMessage: validationError.message,
      canRetry: false,
      suggestions:
        validationError.suggestions || getValidationSuggestions(validationError.validation_errors),
    }
  }

  if (error && typeof error === "object" && "type" in error && error.type === "backend_error") {
    const backendError = error as AppError & { code?: string; details?: Record<string, unknown> }
    return {
      ...backendError,
      severity: determineBackendSeverity(backendError.code),
      category: "server",
      timestamp,
      userMessage: formatBackendUserMessage(backendError),
      technicalMessage: backendError.message,
      canRetry: isRetryableBackendError(backendError.code),
      suggestions: getBackendSuggestions(backendError.code),
    }
  }

  if (error && typeof error === "object" && "type" in error && error.type === "network_error") {
    const networkError = error as AppError & { status?: number; statusText?: string }
    return {
      ...networkError,
      severity: determineNetworkSeverity(networkError.status),
      category: "network",
      timestamp,
      userMessage: formatNetworkUserMessage(networkError),
      technicalMessage: networkError.message,
      canRetry: true,
      suggestions: getNetworkSuggestions(networkError.status),
    }
  }

  if (typeof error === "string") {
    return {
      type: "unknown_error",
      message: error,
      severity: "medium",
      category: "unknown",
      timestamp,
      userMessage: formatStringError(error),
      technicalMessage: error,
      canRetry: true,
      originalError: error,
    }
  }

  if (error instanceof Error) {
    return {
      type: "unknown_error",
      message: error.message,
      severity: "medium",
      category: "unknown",
      timestamp,
      userMessage: formatErrorObject(error),
      technicalMessage: error.message,
      canRetry: true,
      originalError: error,
    }
  }

  return {
    type: "unknown_error",
    message: "An unexpected error occurred",
    severity: "medium",
    category: "unknown",
    timestamp,
    userMessage: "Something went wrong. Please try again.",
    technicalMessage: String(error),
    canRetry: true,
    originalError: error,
  }
}

/**
 * Determine severity based on validation errors
 */
function determineValidationSeverity(validationErrors: string[]): ErrorSeverity {
  const highSeverityPatterns = [
    /xss/i,
    /script/i,
    /javascript:/i,
    /onerror/i,
    /onload/i,
    /dangerous/i,
    /malicious/i,
  ]

  const hasHighSeverity = validationErrors.some(error =>
    highSeverityPatterns.some(pattern => pattern.test(error))
  )

  if (hasHighSeverity) return "high"
  if (validationErrors.length > 3) return "medium"
  return "low"
}

/**
 * Determine severity based on backend error code
 */
function determineBackendSeverity(code?: string): ErrorSeverity {
  if (!code) return "medium"

  const criticalCodes = ["INTERNAL_ERROR", "DATABASE_ERROR", "AUTH_ERROR"]
  const highCodes = ["VALIDATION_ERROR", "RATE_LIMIT", "TIMEOUT"]
  const lowCodes = ["NOT_FOUND", "INVALID_INPUT"]

  if (criticalCodes.includes(code)) return "critical"
  if (highCodes.includes(code)) return "high"
  if (lowCodes.includes(code)) return "low"
  return "medium"
}

/**
 * Determine severity based on network status
 */
function determineNetworkSeverity(status?: number): ErrorSeverity {
  if (!status) return "medium"

  if (status >= 500) return "high"
  if (status >= 400) return "medium"
  return "low"
}

/**
 * Format validation error for user display
 */
function formatValidationUserMessage(
  error: AppError & { validation_errors: string[]; suggestions?: string[] }
): string {
  return error.message
}

/**
 * Format backend error for user display
 */
function formatBackendUserMessage(error: AppError & { code?: string }): string {
  const code = error.code || "UNKNOWN_ERROR"

  switch (code) {
    case "INVALID_API_KEY":
      return "There's an issue with the API configuration. Please contact support."
    case "RATE_LIMIT":
      return "You're sending requests too quickly. Please wait a moment before trying again."
    case "DATABASE_ERROR":
      return "There's a temporary issue with the database. Please try again in a few moments."
    case "TIMEOUT":
      return "The request took too long to process. Please try again with a simpler question."
    default:
      return "Something went wrong on our end. Please try again."
  }
}

/**
 * Format network error for user display
 */
function formatNetworkUserMessage(
  error: AppError & { status?: number; statusText?: string }
): string {
  const status = error.status

  if (status === 0) {
    return "Cannot connect to the server. Please check your internet connection."
  }

  if (status === 404) {
    return "The requested service is not available. Please try again later."
  }

  if (status === 500) {
    return "The server is experiencing issues. Please try again in a few moments."
  }

  if (status && status >= 400 && status < 500) {
    return "There was an issue with your request. Please check your input and try again."
  }

  if (status && status >= 500) {
    return "The server is temporarily unavailable. Please try again later."
  }

  return "Network error occurred. Please check your connection and try again."
}

/**
 * Format string error for user display
 */
function formatStringError(error: string): string {
  if (error.includes("invalid_api_key") || error.includes("Incorrect API key")) {
    return "Invalid API key. Please check your backend configuration."
  }

  if (error.includes("ECONNREFUSED") || error.includes("Cannot connect")) {
    return "Cannot connect to backend. Make sure it's running on http://localhost:8000"
  }

  if (error.includes("database") || error.includes("Connection refused")) {
    return "Database connection error. Please check if PostgreSQL is running."
  }

  if (error.includes("Error processing query:")) {
    return "Failed to process your query. Please try again."
  }

  return error.length > 100 ? "An error occurred. Please try again." : error
}

/**
 * Format Error object for user display
 */
function formatErrorObject(error: Error): string {
  return formatStringError(error.message)
}

/**
 * Get validation suggestions based on errors
 */
function getValidationSuggestions(validationErrors: string[]): string[] {
  const _suggestions: string[] = []

  if (validationErrors.some(err => err.includes("xss") || err.includes("script"))) {
    _suggestions.push("Avoid using HTML tags or script elements in your questions")
    _suggestions.push("Try asking your question in plain text")
  }

  if (validationErrors.some(err => err.includes("javascript:"))) {
    _suggestions.push("Avoid using technical programming terms")
    _suggestions.push("Try rephrasing your question in natural language")
  }

  if (validationErrors.some(err => err.includes("database"))) {
    _suggestions.push("Avoid using technical database terms in your question")
    _suggestions.push("Try asking about your data in business terms")
  }

  if (_suggestions.length === 0) {
    _suggestions.push("Please rephrase your question and try again")
  }

  return _suggestions
}

/**
 * Get backend suggestions based on error code
 */
function getBackendSuggestions(code?: string): string[] {
  switch (code) {
    case "RATE_LIMIT":
      return ["Wait a few seconds before trying again", "Try asking a simpler question"]
    case "TIMEOUT":
      return ["Try breaking your question into smaller parts", "Ask a more specific question"]
    case "DATABASE_ERROR":
      return ["Try again in a few moments", "Contact support if the issue persists"]
    default:
      return ["Please try again", "Contact support if the issue persists"]
  }
}

/**
 * Get network suggestions based on status
 */
function getNetworkSuggestions(status?: number): string[] {
  if (status === 0) {
    return ["Check your internet connection", "Try refreshing the page"]
  }

  if (status && status >= 500) {
    return ["Try again in a few moments", "Check if the service is down"]
  }

  return ["Check your connection", "Try refreshing the page"]
}

/**
 * Check if backend error is retryable
 */
function isRetryableBackendError(code?: string): boolean {
  const retryableCodes = ["RATE_LIMIT", "TIMEOUT", "DATABASE_ERROR", "NETWORK_ERROR"]
  return code ? retryableCodes.includes(code) : true
}

/**
 * Check if error should be shown in toast
 */
export function shouldShowInToast(error: EnhancedError): boolean {
  return error.severity !== "low" || error.category === "validation"
}
