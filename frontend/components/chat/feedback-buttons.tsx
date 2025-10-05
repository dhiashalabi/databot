"use client"

import { ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { MessageFeedback } from "@/types"

interface FeedbackButtonsProps {
  messageId: string
  currentFeedback?: MessageFeedback
  onFeedback: (messageId: string, rating: "positive" | "negative") => void
  disabled?: boolean
}

export function FeedbackButtons({
  messageId,
  currentFeedback,
  onFeedback,
  disabled = false,
}: FeedbackButtonsProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFeedback = async (rating: "positive" | "negative") => {
    if (isSubmitting || disabled) return

    setIsSubmitting(true)
    try {
      await onFeedback(messageId, rating)
    } finally {
      setIsSubmitting(false)
    }
  }

  const isPositiveActive = currentFeedback?.rating === "positive"
  const isNegativeActive = currentFeedback?.rating === "negative"

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleFeedback("positive")}
        disabled={isSubmitting || disabled}
        className={cn(
          "h-7 w-7 p-0 text-muted-foreground hover:text-green-600",
          isPositiveActive && "text-green-600 bg-green-50 hover:bg-green-100"
        )}
        title={isPositiveActive ? "Feedback submitted" : "Helpful response"}
      >
        <ThumbsUp className="h-4 w-4" />
      </Button>

      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleFeedback("negative")}
        disabled={isSubmitting || disabled}
        className={cn(
          "h-7 w-7 p-0 text-muted-foreground hover:text-red-600",
          isNegativeActive && "text-red-600 bg-red-50 hover:bg-red-100"
        )}
        title={isNegativeActive ? "Feedback submitted" : "Not helpful"}
      >
        <ThumbsDown className="h-4 w-4" />
      </Button>
    </div>
  )
}
