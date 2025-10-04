"use client"

import Image from "next/image"
import React from "react"
import ReactMarkdown from "react-markdown"
import rehypeRaw from "rehype-raw"
import remarkGfm from "remark-gfm"

import { ErrorDisplay, ValidationErrorDisplay } from "./error-display"

import { enhanceError } from "@/lib/error-utils"
import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

function processImageUrl(src: string): string {
  let imageUrl = src.replace(/^sandbox:/, "")
  if (imageUrl.startsWith("http")) {
    imageUrl = imageUrl.replace(/^https?:\/\/[^/]+/, "http://localhost:8000")
  } else {
    imageUrl = `http://localhost:8000${imageUrl}`
  }
  return imageUrl
}

interface MessageContentProps {
  content: string
  isUser: boolean
  data?: unknown
  error?: EnhancedError | unknown
}

function SimpleChartImage({ src, alt }: { src: string; alt?: string }) {
  if (!src || typeof src !== "string") {
    return null
  }

  const imageUrl = processImageUrl(src)

  return (
    <Image
      src={imageUrl}
      className="max-w-full h-auto rounded-md"
      alt={alt || "Chart"}
      width={1000}
      height={1000}
      onError={e => {
        e.currentTarget.style.opacity = "0.5"
      }}
    />
  )
}

function EnhancedChartImage({ src, alt, metadata }: { src: string; alt?: string; metadata?: any }) {
  if (!src || typeof src !== "string") {
    return null
  }

  const imageUrl = processImageUrl(src)

  return (
    <div className="my-6 flex flex-col items-center">
      <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
        <Image
          src={imageUrl}
          alt={alt || "Generated Chart"}
          className="max-w-full h-auto rounded-md"
          width={1000}
          height={1000}
          onError={e => {
            e.currentTarget.style.opacity = "0.5"
          }}
        />

        {metadata && (
          <div className="mt-3 space-y-1">
            {metadata.title && (
              <p className="text-sm font-medium text-foreground text-center">{metadata.title}</p>
            )}
            {(metadata.x_label || metadata.y_label) && (
              <p className="text-xs text-muted-foreground text-center">
                {metadata.x_label && metadata.y_label
                  ? `${metadata.x_label} vs ${metadata.y_label}`
                  : metadata.x_label || metadata.y_label}
              </p>
            )}
            {(metadata.total_revenue || metadata.avg_revenue) && (
              <div className="flex justify-center space-x-4 text-xs text-muted-foreground">
                {metadata.total_revenue && (
                  <span>Total: ${metadata.total_revenue.toLocaleString()}</span>
                )}
                {metadata.avg_revenue && <span>Avg: ${metadata.avg_revenue.toLocaleString()}</span>}
              </div>
            )}
          </div>
        )}
      </div>

      {alt && !metadata?.title && (
        <p className="mt-2 text-sm text-muted-foreground text-center">{alt}</p>
      )}
    </div>
  )
}

export function MessageContent({ content, isUser, data: _data, error }: MessageContentProps) {
  const processedContent = !isUser
    ? content.replace(/!\[([^\]]*)\]\(sandbox:([^)]+)\)/g, "![$1]($2)")
    : content

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
            rehypePlugins={[rehypeRaw]}
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
              img: ({ src, alt }) => {
                if (!src || typeof src !== "string") return null

                return <SimpleChartImage src={src} alt={alt} />
              },
            }}
          >
            {processedContent}
          </ReactMarkdown>
        </div>
      )}

      {_data &&
      typeof _data === "object" &&
      _data !== null &&
      "chart_url" in _data &&
      (_data as any).chart_url &&
      !content.includes("![") ? (
        <div className="pt-4">
          <EnhancedChartImage
            src={(_data as any).chart_url}
            alt={(_data as any).metadata?.title || "Generated Chart"}
            metadata={(_data as any).metadata}
          />
        </div>
      ) : null}
    </div>
  )
}
