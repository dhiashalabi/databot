"use client"

import { useCallback } from "react"
import { v4 as uuidv4 } from "uuid"

import { enhanceError, shouldShowInToast } from "@/lib/error-utils"
import { useChatStore } from "@/lib/stores"
import { showErrorToast } from "@/lib/toast-utils"
import type { ChatApiResponse } from "@/types/api-types"
import type { Message } from "@/types/chat-types"

export function useChat() {
  const {
    messages,
    isLoading,
    error,
    selectedModel,
    addMessage,
    setLoading,
    setError,
    setSelectedModel,
    clearMessages,
  } = useChatStore()

  const sendMessage = useCallback(
    async (content: string) => {
      const userMessage: Message = {
        id: uuidv4(),
        role: "user",
        content,
        timestamp: new Date(),
      }

      addMessage(userMessage)
      setLoading(true)
      setError(null)

      const assistantMessageId = uuidv4()

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: content, model: selectedModel || undefined }),
        })

        const data: ChatApiResponse = await response.json()

        if ("error" in data) {
          const enhancedError = enhanceError(data.error.error)

          if (shouldShowInToast(enhancedError)) {
            showErrorToast(enhancedError)
          }

          const errorMessage: Message = {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            timestamp: new Date(),
            error: enhancedError,
          }

          addMessage(errorMessage)
          setLoading(false)
          setError(enhancedError.userMessage)
          return
        }

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`)
        }

        const assistantMessage: Message = {
          id: assistantMessageId,
          role: "assistant",
          content: data.answer || "No response received",
          timestamp: new Date(),
          isTyping: false,
          data: data.data || null,
        }

        addMessage(assistantMessage)
        setLoading(false)
      } catch (error) {
        const rawError = error instanceof Error ? error.message : "An error occurred"
        const enhancedError = enhanceError(rawError)

        if (shouldShowInToast(enhancedError)) {
          showErrorToast(enhancedError)
        }

        const errorMessage: Message = {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          timestamp: new Date(),
          error: enhancedError,
        }

        addMessage(errorMessage)
        setLoading(false)
        setError(enhancedError.userMessage)
      }
    },
    [addMessage, setError, setLoading, selectedModel]
  )

  const clearMessagesCallback = useCallback(() => {
    clearMessages()
  }, [clearMessages])

  const handleModelChange = useCallback(
    (modelId: string) => {
      setSelectedModel(modelId)
    },
    [setSelectedModel]
  )

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages: clearMessagesCallback,
    selectedModel,
    onModelChange: handleModelChange,
  }
}
