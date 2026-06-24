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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5050/api";

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
        {/* Username/Email */}
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748B]" />
          <Input
            type="text"
            placeholder="Tên đăng nhập hoặc Email trường học"
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

      {/* Google Login Button */}
      <Button
        type="button"
        variant="outline"
        onClick={() => {
          window.location.href = `${API_BASE_URL}/auth/google/login?remember_me=${remember}`;
        }}
        className="w-full h-11 bg-white hover:bg-[#F8FAFC] border-[#E2E8F0] text-[#0F172A] font-medium flex items-center justify-center gap-3 mb-6"
        disabled={isLocked}
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="#EA4335"
            d="M5.266 9.765A7.077 7.077 0 0 1 12 4.909c1.69 0 3.218.6 4.418 1.582L19.91 3C17.782 1.145 15.055 0 12 0 7.336 0 3.336 2.673 1.336 6.573L5.266 9.765z"
          />
          <path
            fill="#4285F4"
            d="M23.491 12.273c0-.818-.073-1.609-.209-2.373H12v4.509h6.445c-.277 1.482-1.118 2.74-2.377 3.582l3.873 3c2.264-2.09 3.55-5.173 3.55-8.718z"
          />
          <path
            fill="#FBBC05"
            d="M5.266 14.235A7.025 7.025 0 0 1 4.909 12c0-.79.136-1.545.357-2.235L1.336 6.573A11.934 11.934 0 0 0 0 12c0 1.927.455 3.745 1.255 5.373l4.01-3.138z"
          />
          <path
            fill="#34A853"
            d="M12 24c3.245 0 5.973-1.073 7.964-2.909l-3.873-3c-1.073.718-2.445 1.145-4.09 1.145-3.155 0-5.827-2.127-6.782-5.027L1.255 17.345A11.954 11.954 0 0 0 12 24z"
          />
        </svg>
        Đăng nhập với Google
      </Button>

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
  onSubmit?: (data: {
    ten_dang_nhap: string
    email: string
    password: string
    ho: string
    ten: string
    dien_thoai: string
    gioi_tinh: string
  }) => void
  onLoginClick?: () => void
}

export function RegisterForm({ onSubmit, onLoginClick }: RegisterFormProps) {
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [lastName, setLastName] = useState("")
  const [firstName, setFirstName] = useState("")
  const [phone, setPhone] = useState("")
  const [gender, setGender] = useState("Nam")
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) {
      alert("Mật khẩu xác nhận không khớp")
      return
    }
    onSubmit?.({
      ten_dang_nhap: username,
      email,
      password,
      ho: lastName,
      ten: firstName,
      dien_thoai: phone,
      gioi_tinh: gender
    })
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
        <div className="flex gap-4">
          <Input
            type="text"
            placeholder="Họ và tên đệm"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            required
          />
          <Input
            type="text"
            placeholder="Tên"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
            required
          />
        </div>

        <Input
          type="text"
          placeholder="Tên đăng nhập"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
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

        <Input
          type="text"
          placeholder="Số điện thoại"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          className="h-11 bg-white border-[#E2E8F0] focus:border-[#0EA5E9] focus:ring-[#0EA5E9]"
          required
        />

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-[#64748B] pl-1">Giới tính</label>
          <select
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="flex h-11 w-full rounded-md border border-[#E2E8F0] bg-white px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-[#0F172A]"
          >
            <option value="Nam">Nam</option>
            <option value="Nữ">Nữ</option>
            <option value="Khác">Khác</option>
          </select>
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

      {/* Divider */}
      <div className="flex items-center gap-4 my-6">
        <div className="flex-1 h-px bg-[#E2E8F0]" />
        <span className="text-sm text-[#64748B]">hoặc</span>
        <div className="flex-1 h-px bg-[#E2E8F0]" />
      </div>

      {/* Google Register Button */}
      <Button
        type="button"
        variant="outline"
        onClick={() => {
          window.location.href = `${API_BASE_URL}/auth/google/login?mode=auto_register`;
        }}
        className="w-full h-11 bg-white hover:bg-[#F8FAFC] border-[#E2E8F0] text-[#0F172A] font-medium flex items-center justify-center gap-3 mb-6"
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24">
          <path
            fill="#EA4335"
            d="M5.266 9.765A7.077 7.077 0 0 1 12 4.909c1.69 0 3.218.6 4.418 1.582L19.91 3C17.782 1.145 15.055 0 12 0 7.336 0 3.336 2.673 1.336 6.573L5.266 9.765z"
          />
          <path
            fill="#4285F4"
            d="M23.491 12.273c0-.818-.073-1.609-.209-2.373H12v4.509h6.445c-.277 1.482-1.118 2.74-2.377 3.582l3.873 3c2.264-2.09 3.55-5.173 3.55-8.718z"
          />
          <path
            fill="#FBBC05"
            d="M5.266 14.235A7.025 7.025 0 0 1 4.909 12c0-.79.136-1.545.357-2.235L1.336 6.573A11.934 11.934 0 0 0 0 12c0 1.927.455 3.745 1.255 5.373l4.01-3.138z"
          />
          <path
            fill="#34A853"
            d="M12 24c3.245 0 5.973-1.073 7.964-2.909l-3.873-3c-1.073.718-2.445 1.145-4.09 1.145-3.155 0-5.827-2.127-6.782-5.027L1.255 17.345A11.954 11.954 0 0 0 12 24z"
          />
        </svg>
        Đăng ký với Google
      </Button>

      {/* Login Link */}
      <p className="text-center text-sm text-[#64748B]">
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
