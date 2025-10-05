import { NextResponse } from "next/server"
import { withAuth } from "next-auth/middleware"

export default withAuth(
  function middleware(req) {
    const { pathname } = req.nextUrl
    const token = req.nextauth.token

    if (pathname === "/login" && token) {
      return NextResponse.redirect(new URL("/chat", req.url))
    }

    if (pathname.startsWith("/chat") && !token) {
      return NextResponse.redirect(new URL("/login", req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        const { pathname } = req.nextUrl

        if (pathname === "/login") {
          return true
        }

        return !!token
      },
    },
  }
)

export const config = {
  matcher: ["/chat/:path*", "/api/chat/:path*", "/login"],
}
