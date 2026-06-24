"use client"

import { useEffect, useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { apiClient } from "@/lib/api-client"
import { Loader2, AlertCircle, ShieldAlert } from "lucide-react"
import { Button } from "@/components/ui/button"

function CallbackHandler() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)

  useEffect(() => {
    const token = searchParams.get("token")
    const statusParam = searchParams.get("status")
    const errorParam = searchParams.get("error")

    if (errorParam) {
      setError(errorParam)
      setLoading(false)
      return
    }

    if (statusParam === "pending") {
      setStatus("pending")
      setLoading(false)
      return
    }

    if (token) {
      localStorage.setItem("access_token", token)
      
      // Fetch user info to redirect to appropriate dashboard
      apiClient.get<any>("/users/me")
        .then((user) => {
          if (user.vai_tro === "SINH_VIEN") {
            router.push("/student")
          } else if (user.vai_tro === "GIANG_VIEN") {
            router.push("/lecturer")
          } else {
            router.push("/admin")
          }
        })
        .catch((err) => {
          localStorage.removeItem("access_token")
          setError(err.message || "Không thể tải thông tin người dùng")
          setLoading(false)
        })
    } else {
      setError("Không tìm thấy thông tin đăng nhập")
      setLoading(false)
    }
  }, [searchParams, router])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 text-center">
        <Loader2 className="w-12 h-12 text-[#0EA5E9] animate-spin" />
        <div>
          <h2 className="text-xl font-semibold text-[#0F172A]">Đang xử lý đăng nhập...</h2>
          <p className="text-sm text-[#64748B] mt-1">Vui lòng chờ trong giây lát</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-5 text-center max-w-md p-6 bg-white border border-[#FCA5A5] rounded-xl shadow-lg">
        <div className="w-12 h-12 rounded-full bg-[#FEE2E2] flex items-center justify-center">
          <AlertCircle className="w-6 h-6 text-[#DC2626]" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-[#991B1B]">Đăng nhập thất bại</h2>
          <p className="text-sm text-[#7F1D1D] mt-2 bg-[#FEF2F2] p-3 rounded-lg border border-[#FCA5A5]/40">
            {error === "Google email is not registered in the system" 
              ? "Email Google của bạn chưa được đăng ký trong hệ thống. Vui lòng liên hệ Admin." 
              : error}
          </p>
        </div>
        <Button 
          onClick={() => router.push("/")} 
          className="w-full bg-[#0A2540] hover:bg-[#1A3A5C] text-white"
        >
          Quay lại trang đăng nhập
        </Button>
      </div>
    )
  }

  if (status === "pending") {
    return (
      <div className="flex flex-col items-center justify-center gap-5 text-center max-w-md p-6 bg-white border border-[#93C5FD] rounded-xl shadow-lg">
        <div className="w-12 h-12 rounded-full bg-[#DBEAFE] flex items-center justify-center">
          <ShieldAlert className="w-6 h-6 text-[#1D4ED8]" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-[#1E40AF]">Đăng ký thành công</h2>
          <p className="text-sm text-[#1E3A8A] mt-2 bg-[#EFF6FF] p-3 rounded-lg border border-[#BFDBFE]/50">
            Tài khoản của bạn đã được tạo thành công và đang ở trạng thái chờ kích hoạt. Vui lòng liên hệ quản trị viên để duyệt tài khoản.
          </p>
        </div>
        <Button 
          onClick={() => router.push("/")} 
          className="w-full bg-[#0A2540] hover:bg-[#1A3A5C] text-white"
        >
          Quay lại trang đăng nhập
        </Button>
      </div>
    )
  }

  return null
}

export default function CallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[#F8FAFC]">
      <Suspense fallback={
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <Loader2 className="w-12 h-12 text-[#0EA5E9] animate-spin" />
          <h2 className="text-xl font-semibold text-[#0F172A]">Đang chuẩn bị...</h2>
        </div>
      }>
        <CallbackHandler />
      </Suspense>
    </div>
  )
}
