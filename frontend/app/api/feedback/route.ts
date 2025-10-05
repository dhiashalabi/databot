import { NextRequest, NextResponse } from "next/server"
import type { Session } from "next-auth"
import { getServerSession } from "next-auth/next"

import { authOptions } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const session = (await getServerSession(authOptions)) as Session | null

    if (!session?.accessToken) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()

    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"

    const response = await fetch(`${backendUrl}/api/ai/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.detail || "Failed to submit feedback" },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Feedback API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
