"use client"

import { Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface ChatInputProps {
  input: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onSend: () => void
}

export function ChatInput({ input, isLoading, onInputChange, onKeyDown, onSend }: ChatInputProps) {
  return (
    <div className="border-t border-border bg-background pb-4 pt-4">
      <div className="mx-auto max-w-3xl px-4">
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
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          DataBot can make mistakes. Check important info.
        </p>
      </div>
    </div>
  )
}
