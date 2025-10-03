"use client"

import { useTheme } from "next-themes"
import { Toaster as Sonner, ToasterProps } from "sonner"

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      position="top-center"
      toastOptions={{
        className: "bg-white text-black border border-gray-200 shadow-lg",
        style: {
          opacity: 1,
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
