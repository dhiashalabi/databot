"use client"

import { Bot, Home } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-foreground">
      <div className="mx-auto max-w-2xl text-center">
        <div className="mb-8 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 animate-ping rounded-full bg-violet-500/20" />
            <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-purple-600 shadow-2xl">
              <Bot className="h-12 w-12 text-white" strokeWidth={2} />
            </div>
          </div>
        </div>

        <div className="mb-4">
          <h1 className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-9xl font-bold text-transparent">
            404
          </h1>
        </div>

        <div className="mb-8 space-y-3">
          <h2 className="text-3xl font-semibold text-foreground">Oops! Page Not Found</h2>
          <p className="text-lg text-muted-foreground">
            I searched through all my neural networks, but couldn&apos;t find the page you&apos;re
            looking for.
          </p>
          <div className="mx-auto mt-6 max-w-md rounded-2xl border border-border bg-card p-4">
            <div className="flex items-start gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-purple-600">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <p className="pt-1 text-left text-sm text-muted-foreground">
                The page you&apos;re looking for might have been removed, had its name changed, or
                is temporarily unavailable.
              </p>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <Link href="/">
            <Button className="gap-2 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 px-8 py-6 text-base font-medium text-white hover:from-violet-600 hover:to-purple-700">
              <Home className="h-5 w-5" />
              Back to Home
            </Button>
          </Link>
        </div>

        <div className="mt-12">
          <p className="text-xs text-muted-foreground">
            Error Code: 404 • Page Not Found • DataBot AI Assistant
          </p>
        </div>
      </div>
    </div>
  )
}
