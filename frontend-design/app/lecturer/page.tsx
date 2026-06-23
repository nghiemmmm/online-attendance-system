"use client"

import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { StatusBadge } from "@/components/status-badge"
import { Button } from "@/components/ui/button"
import { 
  Users, 
  Clock,
  BookOpen,
  CalendarCheck,
  TrendingUp,
  Video,
  ArrowRight,
  AlertTriangle
} from "lucide-react"
import Link from "next/link"

const mockUser = {
  name: "Nguyễn Văn B",
  email: "b.nguyen@lecturer.edu.vn",
  avatar: ""
}

const todayClasses = [
  { id: 1, subject: "CS101 - Lập trình Web", time: "08:00 - 10:00", room: "A101", students: 55, session: 8, status: "upcoming" },
  { id: 2, subject: "CS201 - Cơ sở dữ liệu", time: "13:00 - 15:00", room: "B205", students: 45, session: 5, status: "upcoming" },
  { id: 3, subject: "CS301 - Mạng máy tính", time: "15:30 - 17:30", room: "C302", students: 40, session: 3, status: "upcoming" },
]

const recentSessions = [
  { id: 1, subject: "CS101 - Lập trình Web", date: "25/05/2026", present: 50, late: 3, absent: 2 },
  { id: 2, subject: "CS201 - Cơ sở dữ liệu", date: "24/05/2026", present: 42, late: 2, absent: 1 },
  { id: 3, subject: "CS301 - Mạng máy tính", date: "23/05/2026", present: 38, late: 1, absent: 1 },
]

const pendingClaims = [
  { id: 1, student: "Trần Văn C", studentId: "SV001", subject: "CS101", date: "25/05/2026", currentStatus: "absent" as const },
  { id: 2, student: "Lê Thị D", studentId: "SV002", subject: "CS201", date: "24/05/2026", currentStatus: "late" as const },
]

export default function LecturerDashboard() {
  return (
    <AppShell 
      role="lecturer" 
      user={mockUser} 
      breadcrumb="Dashboard"
      notificationCount={pendingClaims.length}
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Lớp học phần</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">5</p>
                  <p className="text-xs text-[#64748B] mt-1">trong học kỳ này</p>
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
                  <p className="text-sm text-[#64748B]">Tổng sinh viên</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">285</p>
                  <p className="text-xs text-[#64748B] mt-1">đăng ký học</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#DCFCE7] flex items-center justify-center">
                  <Users className="w-6 h-6 text-[#22C55E]" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Tỷ lệ có mặt TB</p>
                  <p className="text-3xl font-bold text-[#22C55E] mt-1">91.2%</p>
                  <p className="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    +1.5% so với tháng trước
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
                  <p className="text-sm text-[#64748B]">Khiếu nại chờ</p>
                  <p className="text-3xl font-bold text-[#F59E0B] mt-1">{pendingClaims.length}</p>
                  <p className="text-xs text-[#F59E0B] mt-1">cần xử lý</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#FEF9C3] flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-[#F59E0B]" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Today's Classes */}
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold text-[#0F172A]">
                  Lịch giảng hôm nay
                </CardTitle>
                <span className="text-sm text-[#64748B]">26/05/2026</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {todayClasses.map((cls) => (
                  <div
                    key={cls.id}
                    className="flex items-center justify-between p-3 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-lg bg-[#0A2540] flex items-center justify-center text-white">
                        <span className="text-xs font-medium">B{cls.session}</span>
                      </div>
                      <div>
                        <p className="font-medium text-[#0F172A]">{cls.subject}</p>
                        <div className="flex items-center gap-2 text-sm text-[#64748B]">
                          <span>Phòng {cls.room}</span>
                          <span>•</span>
                          <span>{cls.students} SV</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1 text-[#64748B]">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">{cls.time}</span>
                      </div>
                      <Link href={`/lecturer/live/${cls.id}`}>
                        <Button size="sm" className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                          <Video className="w-4 h-4 mr-1" />
                          Mở lớp
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Sessions */}
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold text-[#0F172A]">
                  Buổi học gần đây
                </CardTitle>
                <Link 
                  href="/lecturer/reports" 
                  className="text-sm text-[#0EA5E9] hover:underline flex items-center gap-1"
                >
                  Xem tất cả
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentSessions.map((session) => (
                  <div
                    key={session.id}
                    className="p-3 border-b border-[#E2E8F0] last:border-0"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-[#0F172A]">{session.subject}</p>
                      <span className="text-sm text-[#64748B]">{session.date}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-[#22C55E]" />
                        <span className="text-sm text-[#64748B]">{session.present} có mặt</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-[#F59E0B]" />
                        <span className="text-sm text-[#64748B]">{session.late} muộn</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-[#EF4444]" />
                        <span className="text-sm text-[#64748B]">{session.absent} vắng</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pending Claims */}
        {pendingClaims.length > 0 && (
          <Card className="border-[#E2E8F0] shadow-sm border-l-4 border-l-[#F59E0B]">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold text-[#0F172A] flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
                  Khiếu nại cần xử lý
                </CardTitle>
                <Link 
                  href="/lecturer/claims" 
                  className="text-sm text-[#0EA5E9] hover:underline flex items-center gap-1"
                >
                  Xem tất cả
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pendingClaims.map((claim) => (
                  <div
                    key={claim.id}
                    className="flex items-center justify-between p-3 bg-[#FEF9C3]/30 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[#0A2540] flex items-center justify-center text-white font-medium">
                        {claim.student.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-[#0F172A]">{claim.student}</p>
                        <p className="text-sm text-[#64748B]">
                          {claim.studentId} • {claim.subject} • {claim.date}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={claim.currentStatus} />
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" className="text-[#22C55E] border-[#22C55E] hover:bg-[#22C55E] hover:text-white">
                          Chấp thuận
                        </Button>
                        <Button size="sm" variant="outline" className="text-[#EF4444] border-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                          Từ chối
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
