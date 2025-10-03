"use client"

import { Bot } from "lucide-react"

import { ModelSelector } from "@/components/model-selector"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface EmptyStateProps {
  input: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onSend: () => void
  onSuggestedQuery: (query: string) => void
  selectedModel: string
  onModelChange: (modelId: string) => void
}

const SUGGESTED_QUERIES = [
  "Compare my sales last month vs this month",
  "Who are my top 10 customers?",
  "What products are low in stock?",
  "Show me pending invoices",
]

export function EmptyState({
  input,
  isLoading,
  onInputChange,
  onKeyDown,
  onSend,
  onSuggestedQuery,
  selectedModel,
  onModelChange,
}: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4">
      <h1 className="mb-12 text-center text-3xl font-medium text-foreground">
        How can I help you today?
      </h1>

      <div className="mb-8 flex items-center gap-3">
        <span className="text-sm font-medium text-muted-foreground">Model:</span>
        <ModelSelector
          selectedModel={selectedModel}
          onModelChange={onModelChange}
          disabled={isLoading}
        />
      </div>

      <div className="w-full max-w-3xl">
        <form
          onSubmit={e => {
            e.preventDefault()
            onSend()
          }}
          className="relative"
        >
          <Textarea
            value={input}
            onChange={e => onInputChange(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask anything..."
            disabled={isLoading}
            rows={1}
            className="min-h-[56px] max-h-[200px] w-full resize-none rounded-3xl border-none bg-muted pl-5 pr-14 pt-4 text-[15px] text-foreground placeholder:text-muted-foreground focus-visible:ring-1 focus-visible:ring-ring"
          />
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            size="icon"
            className="absolute right-2 bottom-2 h-10 w-10 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground"
          >
            <Bot className="h-4 w-4" />
          </Button>
        </form>

        <div className="mt-6 grid grid-cols-2 gap-2">
          {SUGGESTED_QUERIES.map(query => (
            <button
              key={query}
              onClick={() => onSuggestedQuery(query)}
              disabled={isLoading}
              className="rounded-2xl border border-border bg-card px-4 py-3 text-left text-sm text-card-foreground transition-colors hover:bg-accent hover:text-accent-foreground disabled:cursor-not-allowed disabled:opacity-50"
            >
              {query}
            </button>
          ))}
        </div>
      </div>

      <p className="mt-8 text-center text-xs text-muted-foreground">
        DataBot can make mistakes. Check important info.
      </p>
    </div>
  )
}
