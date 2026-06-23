"use client"

import { cn } from "@/lib/utils"
import { Scan } from "lucide-react"

interface LogoProps {
  className?: string
  variant?: "light" | "dark"
  showText?: boolean
  size?: "sm" | "md" | "lg"
}

export function Logo({ className, variant = "dark", showText = true, size = "md" }: LogoProps) {
  const sizeConfig = {
    sm: { icon: "w-6 h-6", text: "text-lg" },
    md: { icon: "w-8 h-8", text: "text-xl" },
    lg: { icon: "w-10 h-10", text: "text-2xl" }
  }

  const colorClass = variant === "light" ? "text-white" : "text-[#0A2540]"

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className={cn("relative", sizeConfig[size].icon)}>
        <Scan className={cn("w-full h-full", colorClass)} strokeWidth={2} />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={cn("w-2 h-2 rounded-full", variant === "light" ? "bg-[#0EA5E9]" : "bg-[#0EA5E9]")} />
        </div>
      </div>
      {showText && (
        <span className={cn("font-bold", sizeConfig[size].text, colorClass)}>
          AttendAI
        </span>
      )}
    </div>
  )
}
