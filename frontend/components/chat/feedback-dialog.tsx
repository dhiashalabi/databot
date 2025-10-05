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
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {isPositive ? (
              <ThumbsUp className="h-5 w-5 text-green-600" />
            ) : (
              <ThumbsDown className="h-5 w-5 text-red-600" />
            )}
            {isPositive ? "Great to hear!" : "Help us improve"}
          </DialogTitle>
          <DialogDescription>
            {isPositive
              ? "Thanks for the positive feedback! Would you like to share what was particularly helpful?"
              : "We're sorry this response wasn't helpful. Please let us know how we can improve."}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="comment">
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
              className="min-h-[100px]"
            />
          </div>
        </div>

        <DialogFooter className="flex gap-2 sm:gap-0">
          <Button variant="outline" onClick={handleSkip} disabled={isSubmitting}>
            Skip
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className={isPositive ? "bg-green-600 hover:bg-green-700" : ""}
          >
            {isSubmitting ? "Submitting..." : "Submit Feedback"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
