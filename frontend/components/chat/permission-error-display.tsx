"use client"

import { AlertTriangle, Shield, UserCheck, Mail } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

interface PermissionErrorDisplayProps {
  error: EnhancedError
  className?: string
}

export function PermissionErrorDisplay({ error, className }: PermissionErrorDisplayProps) {
  const isAIChatError =
    error.message?.includes("AI chat") || error.technicalMessage?.includes("AI chat")
  const isModelError = error.message?.includes("model") || error.technicalMessage?.includes("model")

  return (
    <Card
      className={cn(
        "border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950",
        className
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-orange-500" />
          <CardTitle className="text-orange-800 dark:text-orange-200 text-base">
            Access Permission Required
          </CardTitle>
        </div>
        <CardDescription className="text-orange-700 dark:text-orange-300">
          {isAIChatError
            ? "You need permission to use the AI chat feature."
            : isModelError
              ? "You need permission to use this AI model."
              : "You don't have the required permissions for this action."}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <UserCheck className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-orange-800 dark:text-orange-200">
                What you can do:
              </p>
              <ul className="text-sm text-orange-700 dark:text-orange-300 space-y-1">
                <li>• Contact your system administrator to request access</li>
                <li>• Ask them to assign you a role with AI chat permissions</li>
                <li>• Check if you&apos;re signed in with the correct account</li>
                {isModelError && <li>• Try selecting a different AI model if available</li>}
              </ul>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Mail className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-orange-800 dark:text-orange-200">
                Contact Information:
              </p>
              <p className="text-sm text-orange-700 dark:text-orange-300">
                Reach out to your administrator and mention that you need the &quot;ai.use&quot;
                permission or a role like &quot;analyst&quot;, &quot;manager&quot;, or
                &quot;admin&quot; to access AI chat features.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-orange-200 dark:border-orange-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-orange-600 dark:text-orange-400">
              <AlertTriangle className="h-3 w-3" />
              <span>Error Code: {error.type}</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="text-xs border-orange-300 text-orange-700 hover:bg-orange-100 dark:border-orange-600 dark:text-orange-300 dark:hover:bg-orange-900"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
