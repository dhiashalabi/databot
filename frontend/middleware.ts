import { withAuth } from "next-auth/middleware"

export default withAuth(function middleware(_req) {}, {
  callbacks: {
    authorized: ({ token }) => !!token,
  },
})

export const config = {
  matcher: ["/chat/:path*", "/api/chat/:path*"],
}
