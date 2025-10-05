"use client"

import { ChatContainer } from "@/components/chat"
import { useChat } from "@/hooks/use-chat"

export default function ChatPage() {
  const {
    messages,
    isLoading,
    sendMessage,
    updateMessage,
    clearMessages,
    selectedModel,
    onModelChange,
  } = useChat()

  return (
    <ChatContainer
      messages={messages}
      isLoading={isLoading}
      onSendMessage={sendMessage}
      onUpdateMessage={updateMessage}
      onClearMessages={clearMessages}
      selectedModel={selectedModel}
      onModelChange={onModelChange}
    />
  )
}
