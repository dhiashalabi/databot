import { NextResponse } from "next/server"
import type { Session } from "next-auth"
import { getServerSession } from "next-auth/next"

import { authOptions } from "@/lib/auth"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const session = (await getServerSession(authOptions)) as Session | null

    if (!session?.accessToken) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const response = await fetch(`${BACKEND_URL}/api/health`, {
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.statusText}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error in health check API:", error)

    const errorMessage =
      error instanceof Error
        ? error.message.includes("ECONNREFUSED")
          ? "Cannot connect to backend. Is it running on http://localhost:8000?"
          : error.message
        : "An error occurred"

    return NextResponse.json(
      {
        error: errorMessage,
        status: "error",
        database: "unavailable",
      },
      { status: 500 }
    )
  }
}
