"use client"

import { AlertTriangle, Info, XCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { useUIStore } from "@/lib/stores"
import { cn } from "@/lib/utils"
import type { EnhancedError } from "@/types"

interface ErrorDisplayProps {
  error: EnhancedError
  onDismiss?: () => void
  showTechnicalDetails?: boolean
  className?: string
}

export function ErrorDisplay({
  error,
  onDismiss,
  showTechnicalDetails = false,
  className,
}: ErrorDisplayProps) {
  const { isErrorExpanded, setIsErrorExpanded } = useUIStore()

  const getIcon = () => {
    switch (error.severity) {
      case "critical":
        return <XCircle className="h-5 w-5 text-red-500" />
      case "high":
        return <AlertTriangle className="h-5 w-5 text-orange-500" />
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case "low":
        return <Info className="h-5 w-5 text-blue-500" />
      default:
        return <XCircle className="h-5 w-5 text-gray-500" />
    }
  }

  const getSeverityText = () => {
    switch (error.severity) {
      case "critical":
        return "Critical Error"
      case "high":
        return "High Priority"
      case "medium":
        return "Warning"
      case "low":
        return "Info"
      default:
        return "Error"
    }
  }

  return (
    <div
      className={cn(
        "rounded-lg border p-4 space-y-3",
        {
          "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950":
            error.severity === "critical",
          "border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950":
            error.severity === "high",
          "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950":
            error.severity === "medium",
          "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950":
            error.severity === "low",
          "border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950": !error.severity,
        },
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          {getIcon()}
          <div className="flex-1 space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {getSeverityText()}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{error.category}</span>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{error.userMessage}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-6 w-6 p-0 text-gray-400 hover:text-gray-600"
            >
              <XCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {error.type === "validation_error" &&
        "validation_errors" in error &&
        error.validation_errors.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">Issues found:</h4>
            <ul className="space-y-1">
              {error.validation_errors.map((validationError, index) => (
                <li
                  key={index}
                  className="flex items-start space-x-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>{validationError}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

      {error.suggestions && error.suggestions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">Suggestions:</h4>
          <ul className="space-y-1">
            {error.suggestions.map((suggestion, index) => (
              <li
                key={index}
                className="flex items-start space-x-2 text-sm text-gray-600 dark:text-gray-400"
              >
                <span className="text-blue-500 mt-0.5">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showTechnicalDetails && (
        <Collapsible open={isErrorExpanded} onOpenChange={setIsErrorExpanded}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="text-xs text-gray-500 hover:text-gray-700">
              {isErrorExpanded ? "Hide" : "Show"} technical details
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-2">
            <div className="rounded bg-gray-100 dark:bg-gray-800 p-3 text-xs">
              <div className="space-y-1">
                <div>
                  <strong>Type:</strong> {error.type}
                </div>
                <div>
                  <strong>Message:</strong> {error.technicalMessage}
                </div>
                <div>
                  <strong>Timestamp:</strong> {error.timestamp.toISOString()}
                </div>
                {"originalError" in error && error.originalError ? (
                  <div>
                    <strong>Original Error:</strong> {String(error.originalError)}
                  </div>
                ) : null}
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  )
}

interface ValidationErrorDisplayProps {
  validationErrors: string[]
  suggestions?: string[]
  className?: string
}

export function ValidationErrorDisplay({
  validationErrors,
  suggestions,
  className,
}: ValidationErrorDisplayProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950 p-4 space-y-3",
        className
      )}
    >
      <div className="flex items-start space-x-3">
        <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
        <div className="flex-1 space-y-2">
          <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            Input Validation Issues
          </h4>

          <ul className="space-y-1">
            {validationErrors.map((error, index) => (
              <li
                key={index}
                className="flex items-start space-x-2 text-sm text-yellow-700 dark:text-yellow-300"
              >
                <span className="text-yellow-500 mt-0.5">•</span>
                <span>{error}</span>
              </li>
            ))}
          </ul>

          {suggestions && suggestions.length > 0 && (
            <div className="space-y-1">
              <h5 className="text-xs font-medium text-yellow-800 dark:text-yellow-200">
                Suggestions:
              </h5>
              <ul className="space-y-1">
                {suggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    className="flex items-start space-x-2 text-xs text-yellow-600 dark:text-yellow-400"
                  >
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
