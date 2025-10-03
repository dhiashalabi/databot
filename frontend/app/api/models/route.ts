import { NextResponse } from "next/server"

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`)
    }

    const data = await response.json()

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
