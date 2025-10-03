"use client"

import { Bot } from "lucide-react"

interface MessageAvatarProps {
  isUser: boolean
  isError?: boolean
}

export function MessageAvatar({ isUser, isError = false }: MessageAvatarProps) {
  return (
    <div
      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
        isUser
          ? "bg-muted text-muted-foreground"
          : isError
            ? "bg-amber-500 text-white"
            : "bg-gradient-to-br from-violet-500 to-purple-600 text-white"
      }`}
    >
      {isUser ? <span className="text-xs font-semibold">You</span> : <Bot className="h-4 w-4" />}
    </div>
  )
}
