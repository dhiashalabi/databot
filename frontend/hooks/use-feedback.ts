"use client"

import { useState, useCallback } from "react"
import { toast } from "sonner"
import { v4 as uuidv4 } from "uuid"

import { FeedbackService } from "@/lib/feedback-service"
import type { MessageFeedback, FeedbackRequest } from "@/types"

interface UseFeedbackOptions {
  onFeedbackSubmitted?: (messageId: string, feedback: MessageFeedback) => void
}

export function useFeedback(options: UseFeedbackOptions = {}) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false)
  const [currentFeedback, setCurrentFeedback] = useState<{
    messageId: string
    rating: "positive" | "negative"
  } | null>(null)

  const feedbackService = FeedbackService.getInstance()

  const submitFeedback = useCallback(
    async (request: FeedbackRequest, messageId: string) => {
      setIsSubmitting(true)
      try {
        const result = await feedbackService.submitFeedback(request)

        if (result.success) {
          const feedback: MessageFeedback = {
            id: result.id,
            rating: (request.rating ?? 0) >= 4 ? "positive" : "negative",
            comment: request.feedback_text,
            created_at: new Date(),
          }

          options.onFeedbackSubmitted?.(messageId, feedback)

          toast.success("Thank you for your feedback!", {
            description: "Your feedback helps us improve our AI responses.",
          })

          return feedback
        } else {
          throw new Error(result.message || "Failed to submit feedback")
        }
      } catch (error) {
        console.error("Feedback submission error:", error)
        toast.error("Failed to submit feedback", {
          description: error instanceof Error ? error.message : "Please try again later.",
        })
        return null
      } finally {
        setIsSubmitting(false)
      }
    },
    [feedbackService, options]
  )

  const handleFeedbackClick = useCallback((messageId: string, rating: "positive" | "negative") => {
    setCurrentFeedback({ messageId, rating })
    setFeedbackDialogOpen(true)
  }, [])

  const handleFeedbackSubmit = useCallback(
    async (feedbackData: { rating: "positive" | "negative"; comment?: string }) => {
      if (!currentFeedback) return

      const request: FeedbackRequest = {
        chat_history_id: uuidv4(),
        feedback_type: feedbackData.rating === "positive" ? "thumbs_up" : "thumbs_down",
        rating: feedbackData.rating === "positive" ? 5 : 1,
        is_liked: feedbackData.rating === "positive",
        feedback_text: feedbackData.comment,
      }

      await submitFeedback(request, currentFeedback.messageId)
      setCurrentFeedback(null)
    },
    [currentFeedback, submitFeedback]
  )

  const handleDialogClose = useCallback(() => {
    setFeedbackDialogOpen(false)
    setCurrentFeedback(null)
  }, [])

  return {
    isSubmitting,
    feedbackDialogOpen,
    currentFeedback,
    handleFeedbackClick,
    handleFeedbackSubmit,
    handleDialogClose,
    setFeedbackDialogOpen,
  }
}
