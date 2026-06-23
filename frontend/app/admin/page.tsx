"use client"

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
  ArrowRight
} from "lucide-react"
import Link from "next/link"

const mockUser = {
  name: "Admin System",
  email: "admin@university.edu.vn",
  avatar: ""
}

const recentLogs = [
  { id: 1, user: "GV Nguyễn Văn B", action: "Sửa trạng thái điểm danh", target: "SV002 - Buổi 7 - CS101", time: "14:32:01", type: "edit" },
  { id: 2, user: "SV Trần Văn C", action: "Đăng nhập hệ thống", target: "", time: "14:28:45", type: "login" },
  { id: 3, user: "Admin System", action: "Duyệt dữ liệu khuôn mặt", target: "SV005 - Hoàng Văn E", time: "14:15:20", type: "approve" },
  { id: 4, user: "GV Lê Thị M", action: "Tạo buổi học mới", target: "CS201 - Buổi 6", time: "13:50:10", type: "create" },
]

export default function AdminDashboard() {
  return (
    <AppShell 
      role="admin" 
      user={mockUser} 
      breadcrumb="Dashboard"
      notificationCount={5}
    >
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">
            Bảng điều khiển Quản trị
          </h1>
          <p className="text-[#64748B] mt-1">Học kỳ 1 - Năm học 2024-2025</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Tổng người dùng</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">325</p>
                  <p className="text-xs text-[#64748B] mt-1">280 SV • 40 GV • 5 QTV</p>
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
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">48</p>
                  <p className="text-xs text-[#64748B] mt-1">trong học kỳ này</p>
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
                  <p className="text-sm text-[#64748B]">Tỷ lệ điểm danh TB</p>
                  <p className="text-3xl font-bold text-[#22C55E] mt-1">89.5%</p>
                  <p className="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    +2.1% so với HK trước
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
                  <p className="text-sm text-[#64748B]">Khuôn mặt chờ duyệt</p>
                  <p className="text-3xl font-bold text-[#F59E0B] mt-1">12</p>
                  <p className="text-xs text-[#F59E0B] mt-1">cần xử lý</p>
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
                    <p className="text-sm text-[#64748B]">325 tài khoản</p>
                  </div>
                </Link>
                <Link href="/admin/classes">
                  <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                    <BookOpen className="w-8 h-8 text-[#0A2540] mb-2" />
                    <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Lớp học phần</p>
                    <p className="text-sm text-[#64748B]">48 lớp</p>
                  </div>
                </Link>
                <Link href="/admin/faces">
                  <div className="p-4 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors cursor-pointer group">
                    <ScanFace className="w-8 h-8 text-[#0A2540] mb-2" />
                    <p className="font-medium text-[#0F172A] group-hover:text-[#0EA5E9]">Dữ liệu khuôn mặt</p>
                    <p className="text-sm text-[#64748B]">12 chờ duyệt</p>
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
                  <p className="font-medium text-[#991B1B]">23 sinh viên vắng vượt 20%</p>
                  <p className="text-sm text-[#991B1B]/80 mt-1">Cần gửi cảnh báo học vụ</p>
                </div>
                <div className="p-3 bg-[#FEF9C3] rounded-lg">
                  <p className="font-medium text-[#92400E]">12 hồ sơ khuôn mặt chờ duyệt</p>
                  <p className="text-sm text-[#92400E]/80 mt-1">Sinh viên chưa thể điểm danh</p>
                </div>
                <div className="p-3 bg-[#DBEAFE] rounded-lg">
                  <p className="font-medium text-[#1E40AF]">5 khiếu nại chưa được xử lý</p>
                  <p className="text-sm text-[#1E40AF]/80 mt-1">Quá 48 giờ sẽ tự động từ chối</p>
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
              {recentLogs.map((log) => (
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
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
