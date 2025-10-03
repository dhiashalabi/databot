"use client"

import { useCallback } from "react"
import { v4 as uuidv4 } from "uuid"

import {
  enhanceError,
  extractErrorFromResponse,
  isErrorResponse,
  shouldShowInToast,
} from "@/lib/error-utils"
import { useChatStore } from "@/lib/stores"
import { showErrorToast, showValidationErrorToast } from "@/lib/toast-utils"
import { typeTextWithUpdate } from "@/lib/typing-utils"
import type { Message, ApiResponse } from "@/types"

export function useChat() {
  const {
    messages,
    isLoading,
    error,
    selectedModel,
    addMessage,
    updateMessage,
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
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: content, model: selectedModel || undefined }),
        })

        const data: ApiResponse = await response.json()

        if (isErrorResponse(data)) {
          const extractedError = extractErrorFromResponse(data)
          if (extractedError) {
            const enhancedError = enhanceError(extractedError)

            if (shouldShowInToast(enhancedError)) {
              if (
                enhancedError.type === "validation_error" &&
                "validation_errors" in enhancedError
              ) {
                showValidationErrorToast(enhancedError.userMessage)
              } else {
                showErrorToast(enhancedError)
              }
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
        }

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`)
        }

        if ("answer" in data) {
          const assistantMessage: Message = {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            timestamp: new Date(),
            isTyping: true,
          }

          addMessage(assistantMessage)
          setLoading(false)

          await typeTextWithUpdate(
            data.answer || "No response received",
            text => updateMessage(assistantMessageId, { content: text }),
            {
              wordDelay: 30,
              randomDelay: 20,
              onTypingStart: () => updateMessage(assistantMessageId, { isTyping: true }),
              onTypingComplete: () => updateMessage(assistantMessageId, { isTyping: false }),
            }
          )

          if (data.data) {
            updateMessage(assistantMessageId, { data: data.data })
          }
        } else {
          throw new Error("Invalid response format")
        }
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
    [addMessage, setError, setLoading, updateMessage, selectedModel]
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
