"use client"

import { useEffect, useState } from "react"
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
  AlertTriangle,
  Loader2
} from "lucide-react"
import Link from "next/link"
import { LecturerService } from "@/services/lecturer.service"
import { Claim } from "@/types/lecturer"

export default function LecturerDashboard() {
  const [profile, setProfile] = useState<{ name: string; email: string; maCanBo: number } | null>(null)
  const [stats, setStats] = useState({
    lopCount: 0,
    studentCount: 0,
    attendanceRate: 0,
    changeRate: 0,
    claimsCount: 0
  })
  const [todayClasses, setTodayClasses] = useState<any[]>([])
  const [recentSessions, setRecentSessions] = useState<any[]>([])
  const [pendingClaims, setPendingClaims] = useState<Claim[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [processingClaimId, setProcessingClaimId] = useState<string | null>(null)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Fetch lecturer profile
      const prof = await LecturerService.getProfile()
      setProfile(prof)

      if (prof.maCanBo) {
        // 2. Fetch stats and lists in parallel using maCanBo
        const [
          lopCount,
          claimsCount,
          monthlySummary,
          todaySched,
          recentSess,
          allClaims
        ] = await Promise.all([
          LecturerService.getLopHocPhanCount(prof.maCanBo),
          LecturerService.getPendingClaimsCount(prof.maCanBo),
          LecturerService.getMonthlyAttendanceSummary(prof.maCanBo),
          LecturerService.getLichDayToday(),
          LecturerService.getRecentSessions(prof.maCanBo),
          LecturerService.getClaims(prof.maCanBo)
        ])

        // Parse attendance stats
        const currentRate = monthlySummary?.current_month_attendance_rate
          ? Math.round(monthlySummary.current_month_attendance_rate * 10) / 10
          : 0
        const changeVal = monthlySummary?.change_percentage
          ? Math.round(monthlySummary.change_percentage * 10) / 10
          : 0

        // Parse student count: sum of current students in recent sessions or class lists
        // If not available, we can estimate or use a default
        const totalStudents = monthlySummary?.current_month_total_count || 0

        setStats({
          lopCount,
          studentCount: totalStudents,
          attendanceRate: currentRate,
          changeRate: changeVal,
          claimsCount
        })

        // Map today classes
        setTodayClasses(todaySched.map((item: any) => ({
          id: item.ma_buoi_hoc || item.ma_lop_hoc_phan,
          subject: item.ten_hoc_phan || "Môn học",
          time: `${item.gio_bat_dau || "N/A"} - ${item.gio_ket_thuc || "N/A"}`,
          room: "Phòng máy", // Default placeholder
          students: item.so_sinh_vien_co_mat + item.so_sinh_vien_di_muon + item.so_sinh_vien_vang_mat || 0,
          session: item.so_buoi || 1,
          status: item.trang_thai_buoi_hoc === 'DA_KET_THUC' ? 'completed' : 'upcoming'
        })))

        // Map recent sessions
        setRecentSessions(recentSess.map((item: any) => ({
          id: item.ma_lop_hoc_phan,
          subject: item.ten_hoc_phan || "Môn học",
          date: item.ngay_hoc ? new Date(item.ngay_hoc).toLocaleDateString("vi-VN") : "N/A",
          present: item.so_sinh_vien_co_mat || 0,
          late: item.so_sinh_vien_di_muon || 0,
          absent: item.so_sinh_vien_vang_mat || 0
        })))

        // Filter and set pending claims
        setPendingClaims(allClaims.filter(c => c.status === 'pending'))
      }
    } catch (err: any) {
      console.error("Lỗi khi tải thông tin giảng viên:", err)
      setError("Không thể tải thông tin. Vui lòng kiểm tra lại kết nối mạng hoặc đăng nhập lại.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleClaimStatus = async (claimId: string, status: 'approved' | 'rejected') => {
    if (!profile) return
    setProcessingClaimId(claimId)
    try {
      const success = await LecturerService.updateClaimStatus(profile.maCanBo, claimId, status)
      if (success) {
        setPendingClaims(prev => prev.filter(c => c.id !== claimId))
        setStats(prev => ({
          ...prev,
          claimsCount: Math.max(0, prev.claimsCount - 1)
        }))
      } else {
        alert("Không thể cập nhật trạng thái khiếu nại.")
      }
    } catch (err) {
      alert("Đã xảy ra lỗi khi xử lý khiếu nại.")
    } finally {
      setProcessingClaimId(null)
    }
  }

  const userDisplayName = profile ? profile.name : "Giảng viên"
  const userEmail = profile ? profile.email : "loading..."

  return (
    <AppShell 
      role="lecturer" 
      user={{ name: userDisplayName, email: userEmail, avatar: "" }} 
      breadcrumb="Dashboard"
      notificationCount={pendingClaims.length}
    >
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A]">
            Xin chào, {userDisplayName}!
          </h1>
          <p className="text-[#64748B] mt-1">Học kỳ này - Năm học hiện tại</p>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải thông tin dashboard...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle className="w-12 h-12 text-[#EF4444] mb-3" />
              <h3 className="text-lg font-semibold text-[#991B1B] mb-1">Không thể kết nối</h3>
              <p className="text-[#DC2626] mb-4 max-w-md text-sm">{error}</p>
              <Button onClick={loadData} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
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
                      <p className="text-sm text-[#64748B]">Lớp giảng dạy</p>
                      <p className="text-3xl font-bold text-[#0A2540] mt-1">{stats.lopCount}</p>
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
                      <p className="text-sm text-[#64748B]">Tổng lượt ĐD</p>
                      <p className="text-3xl font-bold text-[#0A2540] mt-1">{stats.studentCount}</p>
                      <p className="text-xs text-[#64748B] mt-1">trong tháng này</p>
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
                      <p className="text-3xl font-bold text-[#22C55E] mt-1">{stats.attendanceRate}%</p>
                      <p className={`text-xs mt-1 flex items-center gap-1 ${stats.changeRate >= 0 ? "text-[#22C55E]" : "text-[#EF4444]"}`}>
                        <TrendingUp className="w-3 h-3" />
                        {stats.changeRate >= 0 ? `+${stats.changeRate}` : stats.changeRate}% so với tháng trước
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
                      <p className="text-3xl font-bold text-[#F59E0B] mt-1">{stats.claimsCount}</p>
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
                    <span className="text-sm text-[#64748B]">{new Date().toLocaleDateString("vi-VN")}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {todayClasses.length === 0 ? (
                      <div className="text-center py-6 text-[#64748B] text-sm">
                        Hôm nay không có lịch giảng dạy.
                      </div>
                    ) : (
                      todayClasses.map((cls) => (
                        <div
                          key={cls.id}
                          className="flex items-center justify-between p-3 bg-[#F8FAFC] rounded-lg hover:bg-[#EFF6FF] transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-lg bg-[#0A2540] flex items-center justify-center text-white">
                              <span className="text-xs font-medium">Buổi {cls.session}</span>
                            </div>
                            <div>
                              <p className="font-medium text-[#0F172A]">{cls.subject}</p>
                              <div className="flex items-center gap-2 text-sm text-[#64748B]">
                                <span>{cls.room}</span>
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
                      ))
                    )}
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
                    {recentSessions.length === 0 ? (
                      <div className="text-center py-6 text-[#64748B] text-sm">
                        Chưa có buổi học nào diễn ra gần đây.
                      </div>
                    ) : (
                      recentSessions.map((session, idx) => (
                        <div
                          key={`${session.id}-${idx}`}
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
                      ))
                    )}
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
                            {claim.studentName.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-[#0F172A]">{claim.studentName}</p>
                            <p className="text-sm text-[#64748B]">
                              Mã SV: {claim.studentId} • {claim.subjectName} • Buổi {claim.sessionNumber} • {claim.date}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <StatusBadge status={claim.currentStatus} />
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-[#22C55E] border-[#22C55E] hover:bg-[#22C55E] hover:text-white"
                              onClick={() => handleClaimStatus(claim.id, 'approved')}
                              disabled={processingClaimId === claim.id}
                            >
                              Chấp thuận
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-[#EF4444] border-[#EF4444] hover:bg-[#EF4444] hover:text-white"
                              onClick={() => handleClaimStatus(claim.id, 'rejected')}
                              disabled={processingClaimId === claim.id}
                            >
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
          </>
        )}
      </div>
    </AppShell>
  )
}
