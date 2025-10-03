"use client"

import { Database, Server, Wrench, AlertTriangle, CheckCircle, Shield } from "lucide-react"

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useHealthCheck } from "@/hooks/use-health-check"

interface HealthIndicatorProps {
  isHealthy: boolean
  isLoading: boolean
  error?: string | null
  children: React.ReactNode
  tooltip: string
}

function HealthIndicator({
  isHealthy,
  isLoading,
  error,
  children: _children,
  tooltip,
}: HealthIndicatorProps) {
  if (isLoading) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse" />
          </TooltipTrigger>
          <TooltipContent>
            <p>Loading...</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  if (error || !isHealthy) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="h-2 w-2 rounded-full bg-red-500 flex items-center justify-center">
              <AlertTriangle className="h-1 w-1 text-white" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>{error || tooltip}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="h-2 w-2 rounded-full bg-green-500 flex items-center justify-center">
            <CheckCircle className="h-1 w-1 text-white" />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>{tooltip}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export function HealthStatus() {
  const { database, mcp, isLoading, error } = useHealthCheck()

  return (
    <div className="flex items-center space-x-3">
      <div className="flex items-center space-x-1">
        <Database className="h-4 w-4 text-muted-foreground" />
        <HealthIndicator
          isHealthy={database.status === "connected"}
          isLoading={isLoading}
          error={database.error}
          tooltip={`Database: ${database.status === "connected" ? "Connected" : "Disconnected"}`}
        >
          <Database className="h-4 w-4" />
        </HealthIndicator>
      </div>

      <div className="flex items-center space-x-1">
        <Server className="h-4 w-4 text-muted-foreground" />
        <HealthIndicator
          isHealthy={mcp.client_connection === "connected"}
          isLoading={isLoading}
          error={mcp.error}
          tooltip={`MCP Client: ${mcp.client_connection === "connected" ? "Connected" : "Disconnected"}`}
        >
          <Server className="h-4 w-4" />
        </HealthIndicator>
      </div>

      <div className="flex items-center space-x-1">
        <Wrench className="h-4 w-4 text-muted-foreground" />
        <HealthIndicator
          isHealthy={mcp.server_connection === "connected"}
          isLoading={isLoading}
          error={mcp.error}
          tooltip={`MCP Server: ${mcp.server_connection === "connected" ? "Connected" : "Disconnected"} (${mcp.tools_available} tools)`}
        >
          <Wrench className="h-4 w-4" />
        </HealthIndicator>
      </div>

      <div className="flex items-center space-x-1">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Shield
                className={`h-4 w-4 ${
                  isLoading
                    ? "text-yellow-500 animate-pulse"
                    : error ||
                        database.status !== "connected" ||
                        mcp.client_connection !== "connected" ||
                        mcp.server_connection !== "connected"
                      ? "text-red-500"
                      : "text-green-500"
                }`}
              />
            </TooltipTrigger>
            <TooltipContent>
              <p>
                {isLoading
                  ? "Loading system status..."
                  : error ||
                      database.status !== "connected" ||
                      mcp.client_connection !== "connected" ||
                      mcp.server_connection !== "connected"
                    ? `System unhealthy: ${error || "One or more services disconnected"}`
                    : "System healthy - all services connected"}
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  )
}
