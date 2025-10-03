"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { DataViewer } from "./data-viewer"
import { ErrorDisplay, ValidationErrorDisplay } from "./error-display"

import { enhanceError } from "@/lib/error-utils"
import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

interface MessageContentProps {
  content: string
  isUser: boolean
  data?: unknown
  error?: EnhancedError | unknown
}

export function MessageContent({ content, isUser, data, error }: MessageContentProps) {
  if (error && !isUser) {
    const enhancedError = enhanceError(error)

    if (enhancedError.type === "validation_error" && "validation_errors" in enhancedError) {
      return (
        <div className="flex-1 space-y-2 pt-1">
          <ValidationErrorDisplay
            validationErrors={enhancedError.validation_errors}
            suggestions={enhancedError.suggestions}
          />
        </div>
      )
    }

    return (
      <div className="flex-1 space-y-2 pt-1">
        <ErrorDisplay
          error={enhancedError}
          showTechnicalDetails={enhancedError.severity === "critical"}
        />
      </div>
    )
  }

  return (
    <div className={cn("flex-1 space-y-2 pt-1", isUser && "flex flex-col items-end")}>
      {isUser ? (
        <p className="whitespace-pre-wrap text-[15px] leading-7 text-foreground text-right">
          {content}
        </p>
      ) : (
        <div className="prose prose-invert max-w-none text-[15px] leading-7 text-foreground">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="mb-4 ml-4 list-disc space-y-1">{children}</ul>,
              ol: ({ children }) => (
                <ol className="mb-4 ml-4 list-decimal space-y-1">{children}</ol>
              ),
              li: ({ children }) => <li className="text-foreground">{children}</li>,
              strong: ({ children }) => (
                <strong className="font-semibold text-foreground">{children}</strong>
              ),
              code: ({ children }) => (
                <code className="rounded bg-muted px-1 py-0.5 text-sm">{children}</code>
              ),
              pre: ({ children }) => (
                <pre className="my-4 overflow-x-auto rounded-lg bg-muted p-4">{children}</pre>
              ),
              table: ({ children }) => (
                <div className="my-6 overflow-x-auto">
                  <table className="w-full border-collapse border border-border rounded-lg overflow-hidden">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => <thead className="bg-muted/50">{children}</thead>,
              tbody: ({ children }) => <tbody className="divide-y divide-border">{children}</tbody>,
              tr: ({ children }) => (
                <tr className="hover:bg-muted/30 transition-colors">{children}</tr>
              ),
              th: ({ children }) => (
                <th className="border border-border px-4 py-3 text-left font-semibold text-foreground bg-muted/30">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="border border-border px-4 py-3 text-foreground">{children}</td>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}

      {data ? (
        <div className="pt-4">
          <DataViewer data={data} />
        </div>
      ) : null}
    </div>
  )
}
