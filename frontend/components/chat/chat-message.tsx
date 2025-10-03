"use client"

import { Check, Copy } from "lucide-react"

import { MessageAvatar } from "./message-avatar"
import { MessageContent } from "./message-content"

import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

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
          <MessageContent content={content} isUser={isUser} data={data} error={error} />
          <div className={cn("mt-2 text-xs text-muted-foreground", isUser && "text-right")}>
            {formatTime(timestamp)}
          </div>
          {!isUser && !isTyping && (
            <div className="mt-2">
              <button
                onClick={() => onCopy(content, id)}
                className="flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-transparent text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                title="Copy"
              >
                {copiedId === id ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
