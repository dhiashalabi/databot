import type { FeedbackRequest } from "@/types"

export interface FeedbackResponse {
  id: string
  success: boolean
  message?: string
}

export class FeedbackService {
  private static instance: FeedbackService
  private baseUrl: string

  private constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  }

  static getInstance(): FeedbackService {
    if (!FeedbackService.instance) {
      FeedbackService.instance = new FeedbackService()
    }
    return FeedbackService.instance
  }

  async submitFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return {
        id: data.id,
        success: true,
        message: "Feedback submitted successfully",
      }
    } catch (error) {
      console.error("Failed to submit feedback:", error)
      return {
        id: "",
        success: false,
        message: error instanceof Error ? error.message : "Failed to submit feedback",
      }
    }
  }

  async getFeedbackHistory(days: number = 30): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/ai-feedback/history?days=${days}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("Failed to fetch feedback history:", error)
      return []
    }
  }
}
