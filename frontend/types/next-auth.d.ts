declare module "next-auth" {
  interface Session {
    accessToken?: string
    user: {
      id: string
      username: string
      email: string
      isAdmin?: boolean
    }
  }

  interface User {
    id: string
    username: string
    email: string
    accessToken: string
    isAdmin: boolean
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string
    isAdmin?: boolean
  }
}
