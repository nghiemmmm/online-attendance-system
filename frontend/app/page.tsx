"use client"

import { useState } from "react"
import { LoginForm, RegisterForm, AuthHero } from "@/components/auth-forms"
import { useRouter } from "next/navigation"
import { AuthService } from "@/services/auth.service"
import { apiClient } from "@/lib/api-client"

export default function LoginPage() {
  const [view, setView] = useState<"login" | "register">("login")
  const router = useRouter()

  const handleLogin = async (data: { email: string; password: string; role: string; remember: boolean }) => {
    try {
      await AuthService.login(data.email, data.password, data.remember);
      // Try to fetch profile to know exactly what the user is
      const user = await apiClient.get<any>("/users/me");
      if (user.vai_tro === "SINH_VIEN") {
        router.push("/student")
      } else if (user.vai_tro === "GIANG_VIEN") {
        router.push("/lecturer")
      } else {
        router.push("/admin")
      }
    } catch (err: any) {
      alert("Đăng nhập thất bại: " + (err.message || "Unknown error"));
    }
  }

  const handleRegister = async (data: {
    ten_dang_nhap: string
    email: string
    password: string
    ho: string
    ten: string
    dien_thoai: string
    gioi_tinh: string
  }) => {
    try {
      await AuthService.register({
        ten_dang_nhap: data.ten_dang_nhap,
        email: data.email,
        password: data.password,
        ho: data.ho,
        ten: data.ten,
        dien_thoai: data.dien_thoai,
        gioi_tinh: data.gioi_tinh,
        vai_tro: "SINH_VIEN",
      });
      alert("Đăng ký tài khoản thành công! Hãy đăng nhập.");
      setView("login");
    } catch (err: any) {
      alert("Đăng ký thất bại: " + (err.message || "Lỗi không xác định"));
    }
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
