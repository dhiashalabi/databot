"use client"

import { Download, FileText, FileSpreadsheet, FileImage, File } from "lucide-react"
import Image from "next/image"
import React from "react"
import ReactMarkdown from "react-markdown"
import rehypeRaw from "rehype-raw"
import remarkGfm from "remark-gfm"

import { ErrorDisplay, ValidationErrorDisplay } from "./error-display"

import { Button } from "@/components/ui/button"
import { enhanceError } from "@/lib/error-utils"
import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

const BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

function remarkSandboxLinks() {
  return (tree: any) => {
    const visit = (node: any) => {
      if (node.type === "link" && node.url && node.url.startsWith("sandbox:")) {
        node.data = node.data || {}
        node.data.hProperties = {
          target: "_blank",
          rel: "noopener noreferrer",
          className: "text-primary hover:underline font-medium",
        }
      }
      if (node.children) {
        node.children.forEach(visit)
      }
    }
    visit(tree)
  }
}

function remarkSandboxImages() {
  return (tree: any) => {
    const visit = (node: any) => {
      if (node.type === "image" && node.url) {
        if (node.url.includes("\\")) {
          node.url = node.url.replace(/\\/g, "/")
        }

        node.data = node.data || {}
        node.data.hProperties = {
          className: "max-w-full h-auto rounded-md",
        }
      }
      if (node.children) {
        node.children.forEach(visit)
      }
    }
    visit(tree)
  }
}

function rehypeSandboxLinks() {
  return (tree: any) => {
    const visit = (node: any) => {
      if (
        node.type === "element" &&
        node.tagName === "a" &&
        node.properties?.href?.startsWith("sandbox:")
      ) {
        const processedUrl = processFileUrl(node.properties.href)
        node.properties.href = processedUrl
        node.properties.target = "_blank"
        node.properties.rel = "noopener noreferrer"
        node.properties.className = "text-primary hover:underline font-medium"
      }
      if (node.children) {
        node.children.forEach(visit)
      }
    }
    visit(tree)
  }
}

function rehypeSandboxImages() {
  return (tree: any) => {
    const visit = (node: any) => {
      if (node.type === "element" && node.tagName === "img" && node.properties?.src) {
        const processedSrc = processImageUrl(node.properties.src)
        node.properties.src = processedSrc
        node.properties.className = "max-w-full h-auto rounded-md"
        node.properties.onError = "this.style.opacity='0.5'"
      }
      if (node.children) {
        node.children.forEach(visit)
      }
    }
    visit(tree)
  }
}
function processImageUrl(src: string): string {
  let imageUrl = src

  if (imageUrl.startsWith("sandbox:")) {
    imageUrl = imageUrl.replace(/^sandbox:/, "")
  }

  if (imageUrl.startsWith("http")) {
    imageUrl = imageUrl.replace(/^https?:\/\/[^/]+/, BASE_URL)
  } else {
    imageUrl = `${BASE_URL}${imageUrl}`
  }

  return imageUrl
}

function processFileUrl(url: string): string {
  let fileUrl = url

  if (fileUrl.startsWith("sandbox:")) {
    fileUrl = fileUrl.replace(/^sandbox:/, "")
  }

  if (fileUrl.startsWith("http")) {
    fileUrl = fileUrl.replace(/^https?:\/\/[^/]+/, BASE_URL)
  } else {
    fileUrl = `${BASE_URL}${fileUrl}`
  }

  return fileUrl
}

function getFileIcon(type: string) {
  switch (type.toLowerCase()) {
    case "xlsx":
    case "xls":
    case "csv":
      return <FileSpreadsheet className="h-4 w-4" />
    case "png":
    case "jpg":
    case "jpeg":
    case "gif":
    case "svg":
      return <FileImage className="h-4 w-4" />
    case "txt":
    case "md":
      return <FileText className="h-4 w-4" />
    default:
      return <File className="h-4 w-4" />
  }
}

interface FileDownloadProps {
  url: string
  filename: string
  type?: string
  success?: boolean
  message?: string
  recordCount?: number
  sheets?: string[]
}

function FileDownload({
  url,
  filename,
  type,
  success: _success,
  message,
  recordCount,
  sheets,
}: FileDownloadProps) {
  const fileUrl = processFileUrl(url)
  const fileIcon = getFileIcon(type || filename.split(".").pop() || "")

  const handleDownload = () => {
    window.open(fileUrl, "_blank")
  }

  return (
    <div className="my-4 rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
            {fileIcon}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">{filename}</p>
            {message && <p className="text-xs text-muted-foreground">{message}</p>}
            {recordCount && <p className="text-xs text-muted-foreground">{recordCount} records</p>}
            {sheets && sheets.length > 0 && (
              <p className="text-xs text-muted-foreground">Sheets: {sheets.join(", ")}</p>
            )}
          </div>
        </div>
        <Button onClick={handleDownload} variant="outline" size="sm" className="shrink-0">
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>
    </div>
  )
}

interface MessageContentProps {
  content: string
  isUser: boolean
  data?: unknown
  error?: EnhancedError | unknown
  files?: Array<{
    url: string
    filename: string
    type?: string
    success?: boolean
    message?: string
    recordCount?: number
    sheets?: string[]
  }>
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

function extractFilesFromData(data: unknown): Array<{
  url: string
  filename: string
  type?: string
  success?: boolean
  message?: string
  recordCount?: number
  sheets?: string[]
}> {
  const files: Array<{
    url: string
    filename: string
    type?: string
    success?: boolean
    message?: string
    recordCount?: number
    sheets?: string[]
  }> = []

  if (data && typeof data === "object" && data !== null) {
    if ("files" in data && Array.isArray((data as any).files)) {
      files.push(...(data as any).files)
    }

    if (Array.isArray(data)) {
      data.forEach(item => {
        if (item && typeof item === "object" && "file_url" in item && "filename" in item) {
          files.push({
            url: (item as any).file_url,
            filename: (item as any).filename,
            type: (item as any).type,
            success: (item as any).success,
            message: (item as any).message,
            recordCount: (item as any).record_count,
            sheets: (item as any).sheets,
          })
        }
      })
    }
  }

  return files
}

export function MessageContent({
  content,
  isUser,
  data: _data,
  error,
  files: _files,
}: MessageContentProps) {
  const processedContent = !isUser
    ? content.replace(/!\[([^\]]*)\]\(sandbox:([^)]+)\)/g, "![$1]($2)")
    : content

  const hasSandboxLinks = !isUser && content.includes("sandbox:")

  const dataFiles = !isUser ? extractFilesFromData(_data) : []
  const allFiles = [...dataFiles, ...(_files || [])]

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
            remarkPlugins={[remarkGfm, remarkSandboxLinks, remarkSandboxImages]}
            rehypePlugins={[rehypeRaw, rehypeSandboxLinks, rehypeSandboxImages]}
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
            {processedContent}
          </ReactMarkdown>
        </div>
      )}

      {_data &&
      typeof _data === "object" &&
      _data !== null &&
      "chart_url" in _data &&
      (_data as any).chart_url &&
      typeof (_data as any).chart_url === "string" &&
      !content.includes("![") ? (
        <div className="pt-4">
          <EnhancedChartImage
            src={(_data as any).chart_url}
            alt={(_data as any).metadata?.title || "Generated Chart"}
            metadata={(_data as any).metadata}
          />
        </div>
      ) : null}

      {!hasSandboxLinks && allFiles.length > 0 && (
        <div className="pt-4">
          {allFiles.map((file, index) => (
            <FileDownload
              key={`${file.url}-${index}`}
              url={file.url}
              filename={file.filename}
              type={file.type}
              success={file.success}
              message={file.message}
              recordCount={file.recordCount}
              sheets={file.sheets}
            />
          ))}
        </div>
      )}
    </div>
  )
}
