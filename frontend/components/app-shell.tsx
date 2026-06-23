"use client"

import { cn } from "@/lib/utils"
import { Logo } from "@/components/logo"
import { RoleBadge } from "@/components/status-badge"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
  LayoutDashboard,
  History,
  MessageSquareWarning,
  User,
  Video,
  BookOpen,
  BarChart3,
  CheckSquare,
  Users,
  GraduationCap,
  ScanFace,
  FileText,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell
} from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

type UserRole = "student" | "lecturer" | "admin"

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
}

const navConfig: Record<UserRole, NavItem[]> = {
  student: [
    { icon: LayoutDashboard, label: "Dashboard", href: "/student" },
    { icon: History, label: "Lịch sử điểm danh", href: "/student/history" },
    { icon: MessageSquareWarning, label: "Khiếu nại", href: "/student/claims" },
    { icon: User, label: "Hồ sơ cá nhân", href: "/student/profile" }
  ],
  lecturer: [
    { icon: LayoutDashboard, label: "Dashboard", href: "/lecturer" },
    { icon: Video, label: "Phòng học trực tiếp", href: "/lecturer/live" },
    { icon: BookOpen, label: "Quản lý lớp học", href: "/lecturer/classes" },
    { icon: BarChart3, label: "Thống kê & Báo cáo", href: "/lecturer/reports" },
    { icon: CheckSquare, label: "Duyệt khiếu nại", href: "/lecturer/claims" }
  ],
  admin: [
    { icon: LayoutDashboard, label: "Dashboard", href: "/admin" },
    { icon: Users, label: "Người dùng", href: "/admin/users" },
    { icon: GraduationCap, label: "Lớp học phần", href: "/admin/classes" },
    { icon: ScanFace, label: "Dữ liệu khuôn mặt", href: "/admin/faces" },
    { icon: FileText, label: "Nhật ký hệ thống", href: "/admin/logs" },
    { icon: BarChart3, label: "Báo cáo tổng hợp", href: "/admin/reports" }
  ]
}

interface SidebarProps {
  role: UserRole
  user: {
    name: string
    email: string
    avatar?: string
  }
  className?: string
}

export function Sidebar({ role, user, className }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)
  const navItems = navConfig[role]

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-[#0A2540] text-white transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-60",
        className
      )}
    >
      {/* Logo */}
      <div className={cn("flex items-center h-16 px-4 border-b border-[#1A3A5C]", collapsed && "justify-center")}>
        <Logo variant="light" showText={!collapsed} size={collapsed ? "sm" : "md"} />
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                    isActive
                      ? "bg-[#EFF6FF] text-[#0A2540] border-l-4 border-[#0EA5E9] -ml-0.5"
                      : "text-white/80 hover:bg-[#1A3A5C] hover:text-white",
                    collapsed && "justify-center px-2"
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  <item.icon className="w-5 h-5 shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* User Info */}
      <div className={cn("border-t border-[#1A3A5C] p-4", collapsed && "px-2")}>
        <div className={cn("flex items-center gap-3", collapsed && "flex-col")}>
          <Avatar className="w-10 h-10">
            <AvatarImage src={user.avatar} alt={user.name} />
            <AvatarFallback className="bg-[#0EA5E9] text-white">
              {user.name.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <RoleBadge role={role} className="mt-1" />
            </div>
          )}
        </div>
        <div className={cn("flex gap-2 mt-4", collapsed && "flex-col")}>
          <Button
            variant="ghost"
            size="icon"
            className="text-white/80 hover:text-white hover:bg-[#1A3A5C]"
            title="Cài đặt"
          >
            <Settings className="w-5 h-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-white/80 hover:text-white hover:bg-[#1A3A5C]"
            title="Đăng xuất"
            onClick={() => router.push('/auth/login')}
          >
            <LogOut className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 w-6 h-6 bg-[#0A2540] border border-[#1A3A5C] rounded-full flex items-center justify-center text-white hover:bg-[#1A3A5C] transition-colors"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  )
}

interface TopNavbarProps {
  breadcrumb: string
  user: {
    name: string
    avatar?: string
  }
  notificationCount?: number
}

export function TopNavbar({ breadcrumb, user, notificationCount = 0 }: TopNavbarProps) {
  return (
    <header className="sticky top-0 z-30 h-16 bg-white border-b border-[#E2E8F0] flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-[#0F172A]">{breadcrumb}</h1>
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5 text-[#64748B]" />
          {notificationCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-[#EF4444] text-white text-xs rounded-full flex items-center justify-center">
              {notificationCount > 9 ? "9+" : notificationCount}
            </span>
          )}
        </Button>
        <Avatar className="w-9 h-9 cursor-pointer">
          <AvatarImage src={user.avatar} alt={user.name} />
          <AvatarFallback className="bg-[#0A2540] text-white text-sm">
            {user.name.charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
}

interface AppShellProps {
  role: UserRole
  user: {
    name: string
    email: string
    avatar?: string
  }
  breadcrumb: string
  notificationCount?: number
  children: React.ReactNode
}

export function AppShell({ role, user, breadcrumb, notificationCount, children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar role={role} user={user} />
      <div className="pl-60 transition-all duration-300">
        <TopNavbar breadcrumb={breadcrumb} user={user} notificationCount={notificationCount} />
        <main className="p-6">
          <div className="max-w-[1280px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
