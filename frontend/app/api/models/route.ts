import { NextResponse } from "next/server"
import type { Session } from "next-auth"
import { getServerSession } from "next-auth/next"

import { authOptions } from "@/lib/auth"

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const session = (await getServerSession(authOptions)) as Session | null

    if (!session?.accessToken) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const response = await fetch(`${API_BASE_URL}/api/models`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`,
      },
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(
        {
          error: data.detail || data.error || "Failed to fetch available models",
          details: data,
        },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching models:", error)

    return NextResponse.json(
      {
        error: "Failed to fetch available models",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    )
  }
}
