"use client"

import { Trash2 } from "lucide-react"

import { HealthStatus } from "@/components/health-status"
import { ModelSelector } from "@/components/model-selector"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"

interface ChatHeaderProps {
  hasMessages: boolean
  onClearMessages: () => void
  isLoading: boolean
  selectedModel: string
  onModelChange: (modelId: string) => void
}

export function ChatHeader({
  hasMessages,
  onClearMessages,
  isLoading,
  selectedModel,
  onModelChange,
}: ChatHeaderProps) {
  if (!hasMessages) return null

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background">
      <div className="mx-auto flex h-12 max-w-4xl items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <span className="text-lg font-medium text-foreground">DataBot</span>
          <ModelSelector
            selectedModel={selectedModel}
            onModelChange={onModelChange}
            disabled={isLoading}
          />
        </div>
        <div className="flex items-center gap-2">
          <HealthStatus />
          <ThemeToggle />
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearMessages}
            disabled={isLoading}
            className="h-8 text-sm"
          >
            <Trash2 className="mr-1.5 h-3.5 w-3.5" />
            Clear
          </Button>
        </div>
      </div>
    </header>
  )
}
