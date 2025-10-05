"use client"

import { Check, Copy } from "lucide-react"

import { FeedbackButtons } from "./feedback-buttons"
import { MessageAvatar } from "./message-avatar"
import { MessageContent } from "./message-content"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { EnhancedError, MessageFeedback } from "@/types"

interface ChatMessageProps {
  id: string
  content: string
  isUser: boolean
  data?: unknown
  error?: EnhancedError | unknown
  copiedId: string | null
  onCopy: (text: string, id: string) => void
  timestamp: Date
  isTyping?: boolean
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
  onFeedback?: (messageId: string, rating: "positive" | "negative") => void
}

export function ChatMessage({
  id,
  content,
  isUser,
  data,
  error,
  copiedId,
  onCopy,
  timestamp,
  isTyping,
  files,
  feedback,
  onFeedback,
}: ChatMessageProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  return (
    <div className="group">
      <div className={cn("flex gap-4", isUser && "flex-row-reverse")}>
        <MessageAvatar isUser={isUser} />
        <div className="flex-1">
          <MessageContent
            content={content}
            isUser={isUser}
            data={data}
            error={error}
            files={files}
          />
          <div className={cn("mt-2 text-xs text-muted-foreground", isUser && "text-right")}>
            {formatTime(timestamp)}
          </div>
          {!isUser && !isTyping && (
            <div className="mt-2 flex items-center gap-2">
              <Button
                onClick={() => onCopy(content, id)}
                variant="outline"
                size="icon"
                className="h-7 w-7"
                title="Copy"
              >
                {copiedId === id ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
              {onFeedback && (
                <FeedbackButtons
                  messageId={id}
                  currentFeedback={feedback}
                  onFeedback={onFeedback}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
