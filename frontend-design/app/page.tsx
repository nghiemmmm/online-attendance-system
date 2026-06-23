"use client"

import { useState } from "react"
import { LoginForm, RegisterForm, AuthHero } from "@/components/auth-forms"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [view, setView] = useState<"login" | "register">("login")
  const router = useRouter()

  const handleLogin = (data: { email: string; password: string; role: string; remember: boolean }) => {
    // Demo: redirect based on role
    if (data.role === "student") {
      router.push("/student")
    } else if (data.role === "lecturer") {
      router.push("/lecturer")
    } else {
      router.push("/admin")
    }
  }

  const handleRegister = (data: { name: string; studentId: string; email: string; password: string }) => {
    console.log("Register:", data)
    setView("login")
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Hero */}
      <div className="hidden lg:flex lg:w-[45%]">
        <AuthHero />
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        {view === "login" ? (
          <LoginForm 
            onSubmit={handleLogin}
            onRegisterClick={() => setView("register")}
          />
        ) : (
          <RegisterForm 
            onSubmit={handleRegister}
            onLoginClick={() => setView("login")}
          />
        )}
      </div>
    </div>
  )
}
