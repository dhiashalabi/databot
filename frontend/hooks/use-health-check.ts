import { useQuery } from "@tanstack/react-query"

import type { HealthCheckResponse, HealthStatus } from "@/types"

export const HEALTH_CHECK_QUERY_KEY = ["health-check"] as const

async function checkHealth(): Promise<HealthCheckResponse> {
  const response = await fetch("/api/health")

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.error || `Health check error: ${response.statusText}`)
  }

  return response.json()
}

export function useHealthCheck(): HealthStatus {
  const { data, isLoading, error, refetch, isError, isSuccess } = useQuery({
    queryKey: HEALTH_CHECK_QUERY_KEY,
    queryFn: checkHealth,
    refetchInterval: 30 * 1000,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 1,
    retryDelay: 2000,
    refetchOnWindowFocus: false,
    refetchOnMount: true,
    enabled: true,
  })

  return {
    status: data?.status || "unhealthy",
    service: data?.service || "unknown",
    database: data?.database || { status: "disconnected", error: "No data" },
    mcp: data?.mcp || {
      client_connection: "disconnected",
      server_connection: "disconnected",
      tools_available: 0,
      database_integration: "disabled",
      error: "No data",
    },
    overall_status: data?.overall_status || "unhealthy",
    isLoading,
    error: error?.message || null,
    isError,
    isSuccess,
    refetch,
  }
}
