"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  Users, 
  BookOpen, 
  ScanFace,
  TrendingUp,
  AlertTriangle,
  FileText,
  ArrowRight,
  Loader2
} from "lucide-react"
import Link from "next/link"
import { AdminService } from "@/services/admin.service"

export default function AdminDashboard() {
  const [adminUser, setAdminUser] = useState({
    name: "Admin",
    email: "admin@university.edu.vn",
    avatar: ""
  })
  const [stats, setStats] = useState({
    total_users: 0,
    total_students: 0,
    total_lecturers: 0,
    total_admins: 0,
    total_classes: 0,
    avg_attendance_rate: 0,
    students_without_face: 0
  })
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsData, logsData, profile] = await Promise.all([
        AdminService.getStats(),
        AdminService.getLogs(),
        AdminService.getProfile().catch(() => ({ name: "Admin", email: "admin@university.edu.vn" }))
      ])
      setStats(statsData)
      setLogs(logsData)
      setAdminUser({ ...profile, avatar: "" })
    } catch (err: any) {
      console.error("Lỗi tải thông tin dashboard:", err)
      setError("Không thể tải thông tin thống kê từ máy chủ.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  return (
    <AppShell 
      role="admin" 
      user={adminUser} 
      breadcrumb="Dashboard"
      notificationCount={stats.students_without_face}
    >
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">
            Bảng điều khiển Quản trị
          </h1>
          <p className="text-[#64748B] mt-1">Học kỳ này - Năm học hiện tại</p>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0] shadow-sm">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải số liệu thống kê...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle className="w-12 h-12 text-[#EF4444] mb-3" />
              <h3 className="text-lg font-semibold text-[#991B1B] mb-1">Đã xảy ra lỗi</h3>
              <p className="text-[#DC2626] mb-4 max-w-md text-sm">{error}</p>
              <Button onClick={loadDashboardData} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="border-[#E2E8F0] shadow-sm">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-[#64748B]">Tổng người dùng</p>
                      <p className="text-3xl font-bold text-[#0A2540] mt-1">{stats.total_users}</p>
                      <p className="text-xs text-[#64748B] mt-1">
                        {stats.total_students} SV • {stats.total_lecturers} GV • {stats.total_admins} QTV
                      </p>
                    </div>
                    <div className="w-12 h-12 rounded-full bg-[#DBEAFE] flex items-center justify-center">
                      <Users className="w-6 h-6 text-[#3B82F6]" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-[#64748B]">Lớp học phần</p>
                      <p className="text-3xl font-bold text-[#0A2540] mt-1">{stats.total_classes}</p>
                      <p className="text-xs text-[#64748B] mt-1">đang hoạt động</p>
                    </div>
                    <div className="w-12 h-12 rounded-full bg-[#DCFCE7] flex items-center justify-center">
                      <BookOpen className="w-6 h-6 text-[#22C55E]" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-[#64748B]">Tỷ lệ chuyên cần</p>
                      <p className="text-3xl font-bold text-[#22C55E] mt-1">
                        {Math.round(stats.avg_attendance_rate * 1000) / 10}%
                      </p>
                      <p className="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        Tính từ các phiên đã đóng
                      </p>
                    </div>
                    <div className="w-12 h-12 rounded-full bg-[#DCFCE7] flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-[#22C55E]" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-[#64748B]">SV chưa có mặt</p>
                      <p className="text-3xl font-bold text-[#F59E0B] mt-1">{stats.students_without_face}</p>
                      <p className="text-xs text-[#F59E0B] mt-1">chưa đăng ký khuôn mặt</p>
                    </div>
                    <div className="w-12 h-12 rounded-full bg-[#FEF9C3] flex items-center justify-center">
                      <ScanFace className="w-6 h-6 text-[#F59E0B]" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Quick Actions */}
              <Card className="border-[#E2E8F0] shadow-sm">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-semibold text-[#0F172A]">
                    Truy cập nhanh
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <Link href="/admin/users">
                      <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                        <Users className="w-8 h-8 text-[#0A2540] mb-2" />
                        <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Quản lý người dùng</p>
                        <p className="text-sm text-[#64748B]">{stats.total_users} tài khoản</p>
                      </div>
                    </Link>
                    <Link href="/admin/classes">
                      <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                        <BookOpen className="w-8 h-8 text-[#0A2540] mb-2" />
                        <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Lớp học phần</p>
                        <p className="text-sm text-[#64748B]">{stats.total_classes} lớp</p>
                      </div>
                    </Link>
                    <Link href="/admin/faces">
                      <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                        <ScanFace className="w-8 h-8 text-[#0A2540] mb-2" />
                        <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Dữ liệu khuôn mặt</p>
                        <p className="text-sm text-[#64748B]">{stats.students_without_face} SV chưa có</p>
                      </div>
                    </Link>
                    <Link href="/admin/reports">
                      <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                        <FileText className="w-8 h-8 text-[#0A2540] mb-2" />
                        <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Báo cáo tổng hợp</p>
                        <p className="text-sm text-[#64748B]">Xuất báo cáo</p>
                      </div>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              {/* Warnings */}
              <Card className="border-[#E2E8F0] shadow-sm border-l-4 border-l-[#F59E0B]">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-semibold text-[#0F172A] flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
                      Cảnh báo hệ thống
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-[#FEE2E2] rounded-lg">
                      <p className="font-medium text-[#991B1B]">Cảnh báo chuyên cần</p>
                      <p className="text-sm text-[#991B1B]/80 mt-1">Cần rà soát các sinh viên vắng vượt quá 20% số buổi.</p>
                    </div>
                    {stats.students_without_face > 0 && (
                      <div className="p-3 bg-[#FEF9C3] rounded-lg">
                        <p className="font-medium text-[#92400E]">{stats.students_without_face} sinh viên chưa có ảnh</p>
                        <p className="text-sm text-[#92400E]/80 mt-1">Yêu cầu đăng ký khuôn mặt để bắt đầu điểm danh tự động.</p>
                      </div>
                    )}
                    <div className="p-3 bg-[#DBEAFE] rounded-lg">
                      <p className="font-medium text-[#1E40AF]">Khiếu nại điểm danh</p>
                      <p className="text-sm text-[#1E40AF]/80 mt-1">Các đơn khiếu nại quá hạn cần được nhắc nhở xử lý.</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="border-[#E2E8F0] shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg font-semibold text-[#0F172A]">
                    Hoạt động gần đây
                  </CardTitle>
                  <Link 
                    href="/admin/logs" 
                    className="text-sm text-[#0EA5E9] hover:underline flex items-center gap-1"
                  >
                    Xem tất cả
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {logs.length === 0 ? (
                    <div className="text-center py-6 text-[#64748B] text-sm">
                      Chưa ghi nhận hoạt động nào gần đây.
                    </div>
                  ) : (
                    logs.map((log) => (
                      <div
                        key={log.id}
                        className="flex items-center gap-4 p-3 bg-[#F8FAFC] rounded-lg"
                      >
                        <div className={`w-1 h-10 rounded-full ${
                          log.type === "login" ? "bg-[#3B82F6]" :
                          log.type === "edit" ? "bg-[#F59E0B]" :
                          log.type === "approve" ? "bg-[#22C55E]" : "bg-[#64748B]"
                        }`} />
                        <div className="flex-1">
                          <p className="text-sm">
                            <span className="font-medium text-[#0F172A]">{log.user}</span>
                            <span className="text-[#64748B]"> • {log.action}</span>
                            {log.target && <span className="text-[#64748B]"> → {log.target}</span>}
                          </p>
                        </div>
                        <span className="text-sm text-[#64748B]">{log.time}</span>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppShell>
  )
}
