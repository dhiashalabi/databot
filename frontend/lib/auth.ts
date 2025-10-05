import CredentialsProvider from "next-auth/providers/credentials"

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null
        }

        try {
          const response = await fetch(`${process.env.BACKEND_URL}/api/auth/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password,
            }),
          })

          if (!response.ok) {
            return null
          }

          const data = await response.json()

          const userResponse = await fetch(`${process.env.BACKEND_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${data.access_token}`,
            },
          })

          if (!userResponse.ok) {
            return null
          }

          const user = await userResponse.json()

          return {
            id: user.id,
            username: user.username,
            email: user.email,
            accessToken: data.access_token,
            isAdmin: user.is_admin,
          }
        } catch (error) {
          console.error("Auth error:", error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }: any) {
      if (user) {
        token.accessToken = user.accessToken
        token.isAdmin = user.isAdmin
      }
      return token
    },
    async session({ session, token }: any) {
      if (token) {
        session.accessToken = token.accessToken
        session.user.id = token.sub || ""
        session.user.isAdmin = token.isAdmin
      }
      return session
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt" as const,
  },
  secret: process.env.NEXTAUTH_SECRET,
}
