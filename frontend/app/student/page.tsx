"use client"

import { useEffect, useState } from "react"
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
  ArrowRight,
  Loader2
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { StudentService } from "@/services/student.service"
import { StudentProfile } from "@/types/student"

export default function StudentDashboard() {
  const router = useRouter()
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [schedule, setSchedule] = useState<any[]>([])
  const [attendance, setAttendance] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const [profileData, scheduleData, attendanceData] = await Promise.all([
          StudentService.getProfile(),
          StudentService.getSchedule(),
          StudentService.getAttendance()
        ])
        setProfile(profileData)
        setSchedule(scheduleData)
        setAttendance(attendanceData)
      } catch (err: any) {
        console.error("Error loading dashboard data:", err)
        setError(err.message || "Đã xảy ra lỗi khi tải dữ liệu.")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return (
      <AppShell 
        role="student" 
        user={{ name: "Đang tải", email: "", avatar: "" }} 
        breadcrumb="Dashboard"
      >
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
          <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
          <p className="text-[#64748B] font-medium">Đang tải dữ liệu dashboard...</p>
        </div>
      </AppShell>
    )
  }

  const userDisplayName = profile?.name || "Sinh viên"
  const userEmail = profile?.email || ""

  // Calculate statistics
  const totalSessions = attendance.length
  const presentCount = attendance.filter(a => a.trang_thai === "CO_MAT").length
  const lateCount = attendance.filter(a => a.trang_thai === "DI_MUON").length
  const absentCount = attendance.filter(a => a.trang_thai === "VANG").length
  
  const attendedCount = presentCount + lateCount
  const attendanceRate = totalSessions > 0 ? ((attendedCount / totalSessions) * 100).toFixed(1) : "0.0"

  // Absence warnings (absent count per class > 20% limit or just count absents)
  const absencesByClass: Record<number, { absent: number, total: number, name: string }> = {}
  attendance.forEach(a => {
    const classId = a.ma_lop_hoc_phan
    const className = a.ten_hoc_phan || `Lớp ${classId}`
    if (!absencesByClass[classId]) {
      absencesByClass[classId] = { absent: 0, total: 0, name: className }
    }
    absencesByClass[classId].total++
    if (a.trang_thai === "VANG") {
      absencesByClass[classId].absent++
    }
  })

  // Warning classes list (classes where student missed >= 20% sessions)
  const warningClasses = Object.values(absencesByClass).filter(c => c.absent / c.total >= 0.2)
  const warningText = warningClasses.length > 0 
    ? `${warningClasses.length} môn` 
    : "Không có"

  // Find active session
  const activeSession = schedule.find(item => item.trang_thai === "DANG_DIEN_RA")

  // Map schedule items
  const upcomingClasses = schedule.slice(0, 3).map((item, idx) => ({
    id: item.ma_buoi_hoc || item.ma_lop_hoc_phan || idx,
    maBuoiHoc: item.ma_buoi_hoc,
    subject: item.ten_hoc_phan || `Lớp học phần ${item.ma_lop_hoc_phan}`,
    date: item.ngay_hoc ? new Date(item.ngay_hoc).toLocaleDateString("vi-VN") : "N/A",
    time: `${item.gio_bat_dau?.substring(0, 5) || "08:00"} - ${item.gio_ket_thuc?.substring(0, 5) || "10:00"}`,
    room: "A" + (100 + (item.ma_lop_hoc_phan % 10)), // Simulated room code
    status: item.trang_thai || "CHUA_DIEM_DANH"
  }))

  const getScheduleStatusText = (status: string) => {
    if (status === "DANG_DIEN_RA") return "Dang mo diem danh"
    if (status === "DA_KET_THUC") return "Da ket thuc"
    if (status === "DA_HUY") return "Da huy"
    return "Chua mo diem danh"
  }

  const handleOpenSchedule = (item: typeof upcomingClasses[number]) => {
    if (!item.maBuoiHoc) {
      alert("Buoi hoc nay chua co ma phien diem danh.")
      return
    }

    if (item.status === "DANG_DIEN_RA") {
      router.push(`/student/live?id=${item.maBuoiHoc}`)
      return
    }

    if (item.status === "DA_KET_THUC") {
      alert("Buoi hoc nay da ket thuc. Ban co the xem ket qua trong lich su diem danh.")
      router.push("/student/history")
      return
    }

    if (item.status === "DA_HUY") {
      alert("Buoi hoc nay da bi huy.")
      return
    }

    alert("Giang vien chua mo phien diem danh cho buoi hoc nay.")
  }

  // Map attendance items (most recent first)
  const recentAttendance = [...attendance].reverse().slice(0, 5).map((item, idx) => ({
    id: item.ma_diem_danh || idx,
    subject: item.ten_hoc_phan || `Lớp học phần ${item.ma_lop_hoc_phan}`,
    date: item.ngay_hoc ? new Date(item.ngay_hoc).toLocaleDateString("vi-VN") : "N/A",
    status: item.trang_thai === "CO_MAT" ? "present" as const : item.trang_thai === "DI_MUON" ? "late" as const : "absent" as const
  }))

  // Map streak items (last 10 records)
  const streakDays = attendance.slice(-10).map((item) => ({
    date: item.ngay_hoc ? item.ngay_hoc.substring(5, 10).replace("-", "/") : "N/A",
    status: item.trang_thai === "CO_MAT" ? "present" : item.trang_thai === "DI_MUON" ? "late" : "absent"
  }))

  // Map warning classes to detailed notification items
  const studentNotifications = warningClasses.map((cls, idx) => ({
    id: `warning-absent-${idx}`,
    title: "Cảnh báo cấm thi",
    description: `Môn học phần "${cls.name}" đã nghỉ ${cls.absent}/${cls.total} buổi (${((cls.absent / cls.total) * 100).toFixed(0)}%).`,
    type: "warning" as const,
  }))

  return (
    <AppShell 
      role="student" 
      user={{ name: userDisplayName, email: userEmail, avatar: "" }} 
      breadcrumb="Dashboard"
      notifications={studentNotifications}
    >
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">
            Xin chào, {userDisplayName}!
          </h1>
          <p className="text-[#64748B] mt-1">Học kỳ hiện tại — Năm học 2025-2026</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Tỷ lệ chuyên cần</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">{attendanceRate}%</p>
                  <p className="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    Toàn học kỳ
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
                  <p className="text-sm text-[#64748B]">Tổng buổi đi học</p>
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">{attendedCount}/{totalSessions}</p>
                  <p className="text-xs text-[#64748B] mt-1">Số buổi có mặt + đi muộn</p>
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
                  <p className="text-3xl font-bold text-[#F59E0B] mt-1">{warningText}</p>
                  <p className="text-xs text-[#F59E0B] mt-1">
                    {warningClasses.length > 0 ? "Vượt quá 20% giới hạn vắng" : "Đạt yêu cầu chuyên cần"}
                  </p>
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
                  Lịch học đã đăng ký
                </CardTitle>
                <span className="text-sm text-[#64748B]">Học phần</span>
              </div>
            </CardHeader>
            <CardContent>
              {upcomingClasses.length > 0 ? (
                <div className="space-y-3">
                  {upcomingClasses.map((cls) => (
                    <button
                      key={cls.id}
                      type="button"
                      onClick={() => handleOpenSchedule(cls)}
                      className="flex w-full items-center justify-between p-3 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0EA5E9]"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#0A2540] flex items-center justify-center text-white font-semibold text-sm">
                          LHP
                        </div>
                        <div>
                          <p className="font-medium text-[#0F172A]">{cls.subject}</p>
                          <p className="text-sm text-[#64748B]">{cls.date}</p>
                          <p className={cls.status === "DANG_DIEN_RA" ? "text-xs font-medium text-[#16A34A]" : "text-xs text-[#64748B]"}>
                            {getScheduleStatusText(cls.status)}
                          </p>
                          <p className="text-sm text-[#64748B]">Phòng {cls.room}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 text-[#64748B]">
                          <Clock className="w-4 h-4" />
                          <span className="text-sm">{cls.time}</span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-[#94A3B8]" />
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[#64748B] text-center py-6">Không có lịch học nào được xếp.</p>
              )}
              {activeSession ? (
                <Link href={`/student/live?id=${activeSession.ma_buoi_hoc}`}>
                  <Button className="w-full mt-4 bg-[#22C55E] hover:bg-[#16A34A] text-white font-semibold animate-pulse border border-[#22C55E]">
                    Vào điểm danh: {activeSession.ten_hoc_phan}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              ) : (
                <Link href="/student/live">
                  <Button className="w-full mt-4 bg-[#64748B] hover:bg-[#475569] text-white">
                    Vào phòng học trực tuyến (Giả lập)
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              )}
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
              {recentAttendance.length > 0 ? (
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
              ) : (
                <p className="text-sm text-[#64748B] text-center py-6">Chưa có lịch sử điểm danh nào.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Attendance Streak */}
        {streakDays.length > 0 && (
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-semibold text-[#0F172A]">
                Chuỗi điểm danh các buổi gần đây
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-start gap-4 overflow-x-auto pb-2">
                {streakDays.map((day, index) => (
                  <div key={index} className="flex flex-col items-center gap-2 shrink-0">
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
        )}
      </div>
    </AppShell>
  )
}
