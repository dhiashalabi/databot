"use client"

import { useEffect, useRef } from "react"

import { ChatHeader } from "./chat-header"
import { ChatInput } from "./chat-input"
import { EmptyState } from "./empty-state"
import { MessagesContainer } from "./messages-container"

import { useUIStore } from "@/lib/stores"
import type { Message } from "@/types"

interface ChatContainerProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (content: string) => void
  onClearMessages: () => void
  selectedModel: string
  onModelChange: (modelId: string) => void
}

export function ChatContainer({
  messages,
  isLoading,
  onSendMessage,
  onClearMessages,
  selectedModel,
  onModelChange,
}: ChatContainerProps) {
  const { input, setInput, clearInput, copiedId, setCopiedId } = useUIStore()
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      clearInput()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const hasMessages = messages.length > 0

  return (
    <div className="flex h-screen flex-col bg-background text-foreground">
      <ChatHeader
        hasMessages={hasMessages}
        onClearMessages={onClearMessages}
        isLoading={isLoading}
        selectedModel={selectedModel}
        onModelChange={onModelChange}
      />

      {!hasMessages ? (
        <EmptyState
          input={input}
          isLoading={isLoading}
          onInputChange={setInput}
          onKeyDown={handleKeyDown}
          onSend={handleSend}
          onSuggestedQuery={onSendMessage}
          selectedModel={selectedModel}
          onModelChange={onModelChange}
        />
      ) : (
        <>
          <div
            ref={scrollAreaRef}
            className="flex-1 overflow-y-auto"
            style={{ scrollBehavior: "smooth" }}
          >
            <MessagesContainer
              messages={messages}
              isLoading={isLoading}
              copiedId={copiedId}
              onCopy={copyToClipboard}
            />
          </div>

          <ChatInput
            input={input}
            isLoading={isLoading}
            onInputChange={setInput}
            onKeyDown={handleKeyDown}
            onSend={handleSend}
          />
        </>
      )}
    </div>
  )
}
