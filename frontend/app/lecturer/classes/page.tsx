"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CourseClass } from "@/types/class"
import { ClassService } from "@/services/class.service"
import { LecturerService } from "@/services/lecturer.service"
import { Loader2, AlertCircle, BookOpen, Users, PlayCircle, Plus } from "lucide-react"

export default function LecturerClassesPage() {
  const [profile, setProfile] = useState<{ name: string; email: string; maCanBo: number } | null>(null)
  const [classes, setClasses] = useState<CourseClass[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pendingClaimsCount, setPendingClaimsCount] = useState(0)

  const fetchProfileAndClasses = async () => {
    setLoading(true)
    setError(null)
    try {
      const prof = await LecturerService.getProfile()
      setProfile(prof)
      
      const [classData, claimsCount] = await Promise.all([
        ClassService.getClasses(),
        prof.maCanBo ? LecturerService.getPendingClaimsCount(prof.maCanBo) : Promise.resolve(0)
      ])
      
      setClasses(classData)
      setPendingClaimsCount(claimsCount)
    } catch (err: any) {
      setError(err.message || "Đã xảy ra lỗi.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfileAndClasses()
  }, [])

  const userDisplayName = profile ? profile.name : "Giảng viên"
  const userEmail = profile ? profile.email : "loading..."

  return (
    <AppShell
      role="lecturer"
      user={{ name: userDisplayName, email: userEmail, avatar: "" }}
      breadcrumb="Quản lý lớp học phần"
      notificationCount={pendingClaimsCount}
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Danh sách lớp học phần</h1>
            <p className="text-[#64748B] mt-1">Quản lý và xem thông tin các lớp bạn đang phụ trách</p>
          </div>
          <Button className="bg-[#0A2540] hover:bg-[#1A3A5C] shrink-0">
            <Plus className="w-4 h-4 mr-2" />
            Tạo buổi học mới
          </Button>
        </div>

        {/* State 1: Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0] shadow-sm">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải dữ liệu lớp học phần...</p>
          </div>
        )}

        {/* State 2: Error */}
        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[#FEE2E2] flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-[#EF4444]" />
              </div>
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Đã xảy ra lỗi</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchProfileAndClasses} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại ngay
              </Button>
            </CardContent>
          </Card>
        )}

        {/* State 3: Empty */}
        {!loading && !error && classes.length === 0 && (
          <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
            <CardContent className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-full bg-[#E2E8F0] flex items-center justify-center mb-4">
                <BookOpen className="w-8 h-8 text-[#64748B]" />
              </div>
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Chưa có lớp học phần nào</h3>
              <p className="text-[#64748B] mb-6 max-w-sm">
                Bạn chưa được phân công phụ trách lớp học phần nào trong học kỳ này.
              </p>
              <Button className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                Đăng ký lớp học
              </Button>
            </CardContent>
          </Card>
        )}

        {/* State 4: Success */}
        {!loading && !error && classes.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {classes.map((cls) => (
              <Card key={cls.id} className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg font-semibold text-[#0F172A] line-clamp-1" title={cls.tenHocPhan}>
                        {cls.tenHocPhan}
                      </CardTitle>
                      <p className="text-sm text-[#64748B] mt-1">Mã lớp: {cls.maLop} • {cls.hocKy}</p>
                    </div>
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                      cls.trangThai === 'Đang học' 
                        ? 'bg-[#DCFCE7] text-[#166534]' 
                        : cls.trangThai === 'Đã kết thúc'
                        ? 'bg-[#F1F5F9] text-[#475569]'
                        : 'bg-[#FEF9C3] text-[#854D0E]'
                    }`}>
                      {cls.trangThai}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-5">
                    <div className="flex items-center gap-2 text-sm text-[#64748B] bg-[#F8FAFC] p-3 rounded-lg">
                      <Users className="w-5 h-5 text-[#0EA5E9]" />
                      <span className="font-medium">Sĩ số:</span>
                      <span>{cls.siSoHienTai} / {cls.siSo} sinh viên</span>
                    </div>
                    <div className="flex items-center gap-3 pt-2">
                      <Button className="flex-1 bg-[#0A2540] hover:bg-[#1A3A5C]" disabled={cls.trangThai === 'Đã kết thúc'}>
                        <PlayCircle className="w-4 h-4 mr-2" />
                        Mở phiên
                      </Button>
                      <Button variant="outline" className="flex-1 text-[#0A2540] border-[#E2E8F0] hover:bg-[#F8FAFC] hover:border-[#0A2540]">
                        Xem danh sách
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
