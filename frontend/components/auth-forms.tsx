"use client"

import { useState } from "react"
import { Logo } from "@/components/logo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { cn } from "@/lib/utils"
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  GraduationCap, 
  User, 
  Shield,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Target
} from "lucide-react"
import Link from "next/link"

type UserRole = "student" | "lecturer" | "admin"

interface LoginFormProps {
  onSubmit?: (data: { email: string; password: string; role: UserRole; remember: boolean }) => void
  onRegisterClick?: () => void
  isLocked?: boolean
  lockTimeRemaining?: number
}

export function LoginForm({ onSubmit, onRegisterClick, isLocked = false, lockTimeRemaining = 0 }: LoginFormProps) {
  const [role, setRole] = useState<UserRole>("student")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit?.({ email, password, role, remember })
  }

  const roleOptions: { value: UserRole; icon: React.ElementType; label: string }[] = [
    { value: "student", icon: GraduationCap, label: "Sinh viên" },
    { value: "lecturer", icon: User, label: "Giảng viên" },
    { value: "admin", icon: Shield, label: "Quản trị viên" }
  ]

  return (
    <div className="w-full max-w-[420px]">
      {/* Logo */}
      <div className="flex justify-center mb-8">
        <Logo size="lg" />
      </div>

      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Chào mừng trở lại</h1>
        <p className="text-[#64748B]">Đăng nhập để tiếp tục</p>
      </div>

      {/* Role Selector */}
      <div className="flex bg-[#F1F5F9] rounded-lg p-1 mb-6">
        {roleOptions.map(({ value, icon: Icon, label }) => (
          <button
            key={value}
            type="button"
            onClick={() => setRole(value)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-sm font-medium transition-all",
              role === value
                ? "bg-[#0A2540] text-white shadow-sm"
                : "text-[#64748B] hover:text-[#0F172A]"
            )}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Lock Alert */}
      {isLocked && (
        <div className="mb-6 p-4 bg-[#FEE2E2] border border-[#FCA5A5] rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-[#991B1B]">Tài khoản tạm khóa</p>
            <p className="text-xs text-[#991B1B]/80 mt-1">
              Do đăng nhập sai quá 5 lần. Thử lại sau {Math.ceil(lockTimeRemaining / 60)} phút.
            </p>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email */}
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748B]" />
          <Input
            type="email"
            placeholder="Email trường học của bạn"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="pl-10 h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            disabled={isLocked}
            required
          />
        </div>

        {/* Password */}
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748B]" />
          <Input
            type={showPassword ? "text" : "password"}
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-10 pr-10 h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            disabled={isLocked}
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-[#0F172A]"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        {/* Remember & Forgot */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <Checkbox
              checked={remember}
              onCheckedChange={(checked) => setRemember(checked === true)}
              disabled={isLocked}
            />
            <span className="text-sm text-[#64748B]">Ghi nhớ đăng nhập</span>
          </label>
          <Link href="/forgot-password" className="text-sm text-[#0EA5E9] hover:underline">
            Quên mật khẩu?
          </Link>
        </div>

        {/* Submit */}
        <Button
          type="submit"
          className="w-full h-11 bg-[#0A2540] hover:bg-[#1A3A5C] text-white font-medium"
          disabled={isLocked}
        >
          Đăng nhập
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </form>

      {/* Divider */}
      <div className="flex items-center gap-4 my-6">
        <div className="flex-1 h-px bg-[#E2E8F0]" />
        <span className="text-sm text-[#64748B]">hoặc</span>
        <div className="flex-1 h-px bg-[#E2E8F0]" />
      </div>

      {/* Register Link */}
      <p className="text-center text-sm text-[#64748B]">
        Chưa có tài khoản?{" "}
        <button onClick={onRegisterClick} className="text-[#0EA5E9] hover:underline font-medium">
          Liên hệ quản trị viên
        </button>{" "}
        để được cấp quyền.
      </p>
    </div>
  )
}

interface RegisterFormProps {
  onSubmit?: (data: { name: string; studentId: string; email: string; password: string }) => void
  onLoginClick?: () => void
}

export function RegisterForm({ onSubmit, onLoginClick }: RegisterFormProps) {
  const [name, setName] = useState("")
  const [studentId, setStudentId] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) return
    onSubmit?.({ name, studentId, email, password })
  }

  return (
    <div className="w-full max-w-[420px]">
      {/* Logo */}
      <div className="flex justify-center mb-8">
        <Logo size="lg" />
      </div>

      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-[#0F172A] mb-2">Đăng ký tài khoản</h1>
        <p className="text-[#64748B]">Dành cho sinh viên</p>
      </div>

      {/* Notice */}
      <div className="mb-6 p-4 bg-[#DBEAFE] border border-[#93C5FD] rounded-lg">
        <p className="text-sm text-[#1E40AF]">
          Sau khi đăng ký, quản trị viên sẽ xét duyệt hồ sơ khuôn mặt trước khi bạn có thể điểm danh.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          placeholder="Họ và tên"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
          required
        />

        <Input
          type="text"
          placeholder="Mã sinh viên"
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
          required
        />

        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748B]" />
          <Input
            type="email"
            placeholder="Email trường học"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="pl-10 h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            required
          />
        </div>

        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748B]" />
          <Input
            type={showPassword ? "text" : "password"}
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-10 pr-10 h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[#64748B] hover:text-[#0F172A]"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>

        <Input
          type={showPassword ? "text" : "password"}
          placeholder="Xác nhận mật khẩu"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
          required
        />

        <Button
          type="submit"
          className="w-full h-11 bg-[#0A2540] hover:bg-[#1A3A5C] text-white font-medium"
        >
          Đăng ký tài khoản
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </form>

      {/* Login Link */}
      <p className="text-center text-sm text-[#64748B] mt-6">
        Đã có tài khoản?{" "}
        <button onClick={onLoginClick} className="text-[#0EA5E9] hover:underline font-medium">
          Đăng nhập
        </button>
      </p>
    </div>
  )
}

export function AuthHero() {
  return (
    <div className="relative flex flex-col items-center justify-center h-full bg-gradient-to-br from-[#0A2540] to-[#1A3A5C] text-white p-8 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-[#0EA5E9]/10 rounded-full blur-3xl animate-pulse-ring" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#0EA5E9]/5 rounded-full blur-3xl animate-pulse-ring" style={{ animationDelay: "1s" }} />
      </div>

      {/* Face Mesh Illustration */}
      <div className="relative w-64 h-64 mb-8">
        <svg viewBox="0 0 200 200" className="w-full h-full">
          {/* Face outline */}
          <ellipse
            cx="100"
            cy="100"
            rx="70"
            ry="85"
            fill="none"
            stroke="#0EA5E9"
            strokeWidth="1"
            className="animate-face-scan"
            strokeDasharray="10 5"
          />
          
          {/* Mesh lines */}
          {[...Array(8)].map((_, i) => (
            <line
              key={`h-${i}`}
              x1="30"
              y1={40 + i * 18}
              x2="170"
              y2={40 + i * 18}
              stroke="#0EA5E9"
              strokeWidth="0.5"
              opacity="0.4"
            />
          ))}
          {[...Array(8)].map((_, i) => (
            <line
              key={`v-${i}`}
              x1={30 + i * 20}
              y1="15"
              x2={30 + i * 20}
              y2="185"
              stroke="#0EA5E9"
              strokeWidth="0.5"
              opacity="0.4"
            />
          ))}
          
          {/* Key points */}
          {[
            [100, 70], [65, 75], [135, 75], // eyes
            [100, 110], // nose
            [100, 140], [80, 135], [120, 135], // mouth
          ].map(([cx, cy], i) => (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r="4"
              fill="#0EA5E9"
              className="animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
          
          {/* Scanning rings */}
          <circle
            cx="100"
            cy="100"
            r="90"
            fill="none"
            stroke="#0EA5E9"
            strokeWidth="2"
            opacity="0.3"
            className="animate-pulse-ring"
          />
          <circle
            cx="100"
            cy="100"
            r="100"
            fill="none"
            stroke="#0EA5E9"
            strokeWidth="1"
            opacity="0.2"
            className="animate-pulse-ring"
            style={{ animationDelay: "0.5s" }}
          />
        </svg>
      </div>

      {/* Text content */}
      <div className="relative z-10 text-center max-w-md">
        <h2 className="text-3xl font-bold mb-4 text-balance">
          Điểm danh thông minh — Chính xác tuyệt đối
        </h2>
        <p className="text-slate-300 text-sm mb-8">
          Hệ thống nhận diện khuôn mặt tự động tích hợp WebRTC cho lớp học hiện đại.
        </p>
      </div>

      {/* Trust signals */}
      <div className="relative z-10 flex gap-4">
        <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full backdrop-blur-sm">
          <ShieldCheck className="w-4 h-4 text-[#0EA5E9]" />
          <span className="text-sm">Bảo mật</span>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full backdrop-blur-sm">
          <Zap className="w-4 h-4 text-[#0EA5E9]" />
          <span className="text-sm">Thời gian thực</span>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full backdrop-blur-sm">
          <Target className="w-4 h-4 text-[#0EA5E9]" />
          <span className="text-sm">Chính xác cao</span>
        </div>
      </div>
    </div>
  )
}
