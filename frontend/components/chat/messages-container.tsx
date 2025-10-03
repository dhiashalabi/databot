"use client"

import { useEffect, useRef } from "react"

import { ChatMessage } from "./chat-message"
import { LoadingIndicator } from "./loading-indicator"

import type { Message } from "@/types"

interface MessagesContainerProps {
  messages: Message[]
  isLoading: boolean
  copiedId: string | null
  onCopy: (text: string, id: string) => void
}

export function MessagesContainer({
  messages,
  isLoading,
  copiedId,
  onCopy,
}: MessagesContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <div className="space-y-8">
        {messages.map(message => (
          <ChatMessage
            key={message.id}
            id={message.id}
            content={message.content}
            isUser={message.role === "user"}
            data={message.data}
            error={message.error}
            copiedId={copiedId}
            onCopy={onCopy}
            timestamp={message.timestamp}
            isTyping={message.isTyping}
          />
        ))}

        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
