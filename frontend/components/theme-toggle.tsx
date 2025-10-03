"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { useEffect } from "react"

import { Button } from "@/components/ui/button"
import { useUIStore } from "@/lib/stores"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const { isThemeMounted, setIsThemeMounted } = useUIStore()

  useEffect(() => {
    setIsThemeMounted(true)
  }, [setIsThemeMounted])

  if (!isThemeMounted) {
    return (
      <Button variant="ghost" size="icon" className="h-8 w-8">
        <Sun className="h-4 w-4" />
      </Button>
    )
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="h-8 w-8"
    >
      {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
