export interface ApiResponse {
  answer: string
  data: unknown | null
  query: string
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

export interface ErrorResponse {
  error: {
    answer: string
    data: unknown | null
    query: string
    error: {
      type: "validation_error" | "backend_error"
      message: string
      validation_errors?: string[]
      suggestions?: string[]
      code?: string
      details?: Record<string, unknown>
    }
  }
}

export type ChatApiResponse = ApiResponse | ErrorResponse
