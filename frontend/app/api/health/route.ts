import { NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`)

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
