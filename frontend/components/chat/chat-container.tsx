"use client"

import { useEffect, useRef } from "react"

import { ChatHeader } from "./chat-header"
import { ChatInput } from "./chat-input"
import { EmptyState } from "./empty-state"
import { FeedbackDialog } from "./feedback-dialog"
import { MessagesContainer } from "./messages-container"

import { useFeedback } from "@/hooks/use-feedback"
import { useUIStore } from "@/lib/stores"
import type { Message, MessageFeedback } from "@/types"

interface ChatContainerProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (content: string) => void
  onClearMessages: () => void
  selectedModel: string
  onModelChange: (modelId: string) => void
  onUpdateMessage?: (messageId: string, updates: Partial<Message>) => void
}

export function ChatContainer({
  messages,
  isLoading,
  onSendMessage,
  onClearMessages,
  selectedModel,
  onModelChange,
  onUpdateMessage,
}: ChatContainerProps) {
  const { input, setInput, clearInput, copiedId, setCopiedId } = useUIStore()
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const {
    feedbackDialogOpen,
    currentFeedback,
    handleFeedbackClick,
    handleFeedbackSubmit,
    handleDialogClose,
    isSubmitting,
  } = useFeedback({
    onFeedbackSubmitted: (messageId: string, feedback: MessageFeedback) => {
      onUpdateMessage?.(messageId, { feedback })
    },
  })

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
              onFeedback={handleFeedbackClick}
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

      <FeedbackDialog
        open={feedbackDialogOpen}
        onOpenChange={handleDialogClose}
        rating={currentFeedback?.rating || "positive"}
        onSubmit={handleFeedbackSubmit}
        isSubmitting={isSubmitting}
      />
    </div>
  )
}
