import { GeistSans } from "geist/font/sans"
import type { Metadata } from "next"

import { ErrorBoundary } from "@/components/error-boundary"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/sonner"
import { QueryProvider } from "@/lib/query-client"
import "./globals.css"

export const metadata: Metadata = {
  title: "DataBot - AI Business Assistant",
  description: "Ask anything about your business data",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${GeistSans.className} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ErrorBoundary>
            <QueryProvider>
              {children}
              <Toaster />
            </QueryProvider>
          </ErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  )
}
