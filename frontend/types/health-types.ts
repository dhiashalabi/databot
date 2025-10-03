export interface DatabaseHealth {
  status: "connected" | "disconnected"
  error: string | null
}

export interface MCPHealth {
  client_connection: "connected" | "disconnected"
  server_connection: "connected" | "disconnected"
  tools_available: number
  database_integration: "working" | "no_tools_available" | "no_suitable_tools" | "disabled"
  error: string | null
}

export interface HealthCheckResponse {
  status: "healthy" | "unhealthy"
  service: string
  database: DatabaseHealth
  mcp: MCPHealth
  overall_status: "healthy" | "unhealthy"
}

export interface HealthStatus {
  status: "healthy" | "unhealthy"
  service: string
  database: DatabaseHealth
  mcp: MCPHealth
  overall_status: "healthy" | "unhealthy"
  isLoading: boolean
  error: string | null
  isError: boolean
  isSuccess: boolean
  refetch: () => void
}
