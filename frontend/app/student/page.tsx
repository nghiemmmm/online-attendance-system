"use client"

import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { StatusBadge } from "@/components/status-badge"
import { Button } from "@/components/ui/button"
import { 
  CalendarCheck, 
  AlertTriangle, 
  TrendingUp,
  Clock,
  BookOpen,
  ArrowRight
} from "lucide-react"
import Link from "next/link"

const mockUser = {
  name: "Nguyễn Văn An",
  email: "an.nguyen@student.edu.vn",
  avatar: ""
}

const upcomingClasses = [
  { id: 1, subject: "Lập trình Web", time: "08:00 - 10:00", room: "A101", session: 8 },
  { id: 2, subject: "Cơ sở dữ liệu", time: "13:00 - 15:00", room: "B205", session: 5 },
  { id: 3, subject: "Mạng máy tính", time: "15:30 - 17:30", room: "C302", session: 3 },
]

const recentAttendance = [
  { id: 1, subject: "Lập trình Web", date: "25/05/2026", status: "present" as const },
  { id: 2, subject: "Cơ sở dữ liệu", date: "24/05/2026", status: "present" as const },
  { id: 3, subject: "Mạng máy tính", date: "23/05/2026", status: "late" as const },
  { id: 4, subject: "Lập trình Web", date: "22/05/2026", status: "present" as const },
  { id: 5, subject: "Trí tuệ nhân tạo", date: "21/05/2026", status: "absent" as const },
]

export default function StudentDashboard() {
  return (
    <AppShell 
      role="student" 
      user={mockUser} 
      breadcrumb="Dashboard"
      notificationCount={2}
    >
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">
            Xin chào, {mockUser.name}!
          </h1>
          <p className="text-[#64748B] mt-1">Học kỳ 1 - Năm học 2024-2025</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Tỷ lệ chuyên cần</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">87.5%</p>
                  <p className="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    +2.5% so với tháng trước
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#DCFCE7] flex items-center justify-center">
                  <CalendarCheck className="w-6 h-6 text-[#22C55E]" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Tổng buổi có mặt</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">42/48</p>
                  <p className="text-xs text-[#64748B] mt-1">buổi trong học kỳ</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#DBEAFE] flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-[#3B82F6]" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Cảnh báo vắng</p>
                  <p className="text-3xl font-bold text-[#F59E0B] mt-1">2 môn</p>
                  <p className="text-xs text-[#F59E0B] mt-1">Gần vượt 20% giới hạn</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#FEF9C3] flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-[#F59E0B]" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upcoming Classes */}
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold text-[#0F172A]">
                  Lịch học hôm nay
                </CardTitle>
                <span className="text-sm text-[#64748B]">26/05/2026</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {upcomingClasses.map((cls) => (
                  <div
                    key={cls.id}
                    className="flex items-center justify-between p-3 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-[#0A2540] flex items-center justify-center text-white font-semibold text-sm">
                        B{cls.session}
                      </div>
                      <div>
                        <p className="font-medium text-[#0F172A]">{cls.subject}</p>
                        <p className="text-sm text-[#64748B]">Phòng {cls.room}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-[#64748B]">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">{cls.time}</span>
                    </div>
                  </div>
                ))}
              </div>
              <Link href="/student/live">
                <Button className="w-full mt-4 bg-[#0A2540] hover:bg-[#1A3A5C]">
                  Vào phòng học trực tuyến
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Recent Attendance */}
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold text-[#0F172A]">
                  Điểm danh gần đây
                </CardTitle>
                <Link 
                  href="/student/history" 
                  className="text-sm text-[#0EA5E9] hover:underline flex items-center gap-1"
                >
                  Xem tất cả
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentAttendance.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between py-2 border-b border-[#E2E8F0] last:border-0"
                  >
                    <div>
                      <p className="font-medium text-[#0F172A]">{item.subject}</p>
                      <p className="text-sm text-[#64748B]">{item.date}</p>
                    </div>
                    <StatusBadge status={item.status} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Attendance Streak */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg font-semibold text-[#0F172A]">
              Chuỗi điểm danh 10 buổi gần nhất
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between gap-2">
              {[
                { date: "16/05", status: "present" },
                { date: "17/05", status: "present" },
                { date: "18/05", status: "present" },
                { date: "19/05", status: "late" },
                { date: "20/05", status: "present" },
                { date: "21/05", status: "absent" },
                { date: "22/05", status: "present" },
                { date: "23/05", status: "late" },
                { date: "24/05", status: "present" },
                { date: "25/05", status: "present" },
              ].map((day, index) => (
                <div key={index} className="flex flex-col items-center gap-2">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium ${
                      day.status === "present"
                        ? "bg-[#22C55E]"
                        : day.status === "late"
                        ? "bg-[#F59E0B]"
                        : "bg-[#EF4444]"
                    }`}
                    title={`${day.date}: ${day.status === "present" ? "Có mặt" : day.status === "late" ? "Muộn" : "Vắng"}`}
                  >
                    {day.status === "present" ? "P" : day.status === "late" ? "L" : "V"}
                  </div>
                  <span className="text-xs text-[#64748B]">{day.date}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
