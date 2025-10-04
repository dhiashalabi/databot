export interface ApiResponse {
  answer: string
  data: unknown | null
  query: string
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
