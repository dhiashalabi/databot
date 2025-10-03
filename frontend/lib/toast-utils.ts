import { toast } from "sonner"

import type { EnhancedError } from "@/types"

/**
 * Show enhanced error toast with appropriate styling
 */
export function showErrorToast(error: EnhancedError, options?: { duration?: number }) {
  const { duration = 5000 } = options || {}

  const title = formatErrorTypeToPascalCase(error.type)
  const message = error.userMessage

  if (error.severity === "critical") {
    toast.error(title, {
      duration,
      className: "!bg-red-600 !text-white !border-red-600 [&>*]:!text-white [&_*]:!text-white",
      description: message,
    })
  } else if (error.severity === "high") {
    toast.error(title, {
      duration,
      className:
        "!bg-orange-600 !text-white !border-orange-600 [&>*]:!text-white [&_*]:!text-white",
      description: message,
    })
  } else if (error.severity === "medium") {
    toast.warning(title, {
      duration,
      className:
        "!bg-yellow-600 !text-white !border-yellow-600 [&>*]:!text-white [&_*]:!text-white",
      description: message,
    })
  } else {
    toast.info(title, {
      duration,
      className: "!bg-blue-600 !text-white !border-blue-600 [&>*]:!text-white [&_*]:!text-white",
      description: message,
    })
  }
}

/**
 * Show validation error toast with specific styling
 */
export function showValidationErrorToast(errorMessage?: string) {
  const message =
    errorMessage ||
    "I couldn't process your query due to validation issues. Please try rephrasing your question."
  const title = "Validation Error"

  toast.warning(title, {
    duration: 7000,
    className: "!bg-orange-600 !text-white !border-orange-600 [&>*]:!text-white [&_*]:!text-white",
    description: message,
  })
}

/**
 * Convert error type to Pascal Case
 */
function formatErrorTypeToPascalCase(errorType: string): string {
  return errorType
    .split("_")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}
