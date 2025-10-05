import { useQuery } from "@tanstack/react-query"

import type { ModelsResponse } from "@/types"

export const MODELS_QUERY_KEY = ["models"] as const

async function fetchModels(): Promise<ModelsResponse> {
  const response = await fetch("/api/models", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.error || errorData.message || `Failed to fetch models: ${response.statusText}`
    )
  }

  return response.json()
}

export function useModels() {
  const { data, isLoading, error, refetch, isError, isSuccess } = useQuery({
    queryKey: MODELS_QUERY_KEY,
    queryFn: fetchModels,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 3,
    refetchOnWindowFocus: false,
  })

  return {
    models: data?.models || [],
    defaultModel: data?.default_model || "",
    isLoading,
    error: error?.message || null,
    isError,
    isSuccess,
    refetch,
  }
}

export function useChatModels() {
  const { models, defaultModel, isLoading, error, isError, isSuccess, refetch } = useModels()

  const chatModels = models.filter(
    model =>
      model.id.includes("gpt-") ||
      model.id.includes("o1") ||
      model.id.includes("o3") ||
      model.id.includes("o4")
  )

  return {
    models,
    chatModels,
    defaultModel,
    isLoading,
    error,
    isError,
    isSuccess,
    refetch,
  }
}
