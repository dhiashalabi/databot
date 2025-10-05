"use client"

import { ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

interface FeedbackDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  rating: "positive" | "negative"
  onSubmit: (feedback: { rating: "positive" | "negative"; comment?: string }) => void
  isSubmitting?: boolean
}

export function FeedbackDialog({
  open,
  onOpenChange,
  rating,
  onSubmit,
  isSubmitting = false,
}: FeedbackDialogProps) {
  const [comment, setComment] = useState("")

  const handleSubmit = () => {
    onSubmit({
      rating,
      comment: comment.trim() || undefined,
    })
    setComment("")
    onOpenChange(false)
  }

  const handleSkip = () => {
    onSubmit({ rating })
    setComment("")
    onOpenChange(false)
  }

  const isPositive = rating === "positive"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader className="space-y-3">
          <DialogTitle className="flex items-center gap-3 text-lg">
            {isPositive ? (
              <ThumbsUp className="h-6 w-6 text-green-600" />
            ) : (
              <ThumbsDown className="h-6 w-6 text-red-600" />
            )}
            {isPositive ? "Great to hear!" : "Help us improve"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-relaxed">
            {isPositive
              ? "Thanks for the positive feedback! Would you like to share what was particularly helpful?"
              : "We're sorry this response wasn't helpful. Please let us know how we can improve."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-6">
          <div className="space-y-3">
            <Label htmlFor="comment" className="text-sm font-medium">
              {isPositive ? "What did you like? (optional)" : "What went wrong? (optional)"}
            </Label>
            <Textarea
              id="comment"
              placeholder={
                isPositive
                  ? "The response was accurate, well-structured, helpful..."
                  : "The response was inaccurate, unclear, incomplete..."
              }
              value={comment}
              onChange={e => setComment(e.target.value)}
              className="min-h-[120px] resize-none"
            />
          </div>
        </div>

        <DialogFooter className="flex flex-col-reverse gap-3 sm:flex-row sm:gap-4">
          <Button
            variant="outline"
            onClick={handleSkip}
            disabled={isSubmitting}
            className="w-full sm:w-auto px-6 py-2.5"
          >
            Skip
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className={`w-full sm:w-auto px-6 py-2.5 font-medium ${
              isPositive
                ? "bg-green-600 hover:bg-green-700 focus-visible:ring-green-600/20"
                : "bg-red-600 hover:bg-red-700 focus-visible:ring-red-600/20"
            }`}
          >
            {isSubmitting ? "Submitting..." : "Submit Feedback"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
