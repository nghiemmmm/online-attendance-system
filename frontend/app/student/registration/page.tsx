"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Loader2, BookOpen, Search, Check, AlertCircle } from "lucide-react"
import { StudentService } from "@/services/student.service"
import { StudentProfile } from "@/types/student"

export default function StudentRegistrationPage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [classes, setClasses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [processingId, setProcessingId] = useState<number | null>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const [profileData, classesData] = await Promise.all([
        StudentService.getProfile(),
        StudentService.getAvailableClasses()
      ])
      setProfile(profileData)
      setClasses(classesData)
    } catch (err: any) {
      console.error("Error loading registration data:", err)
      setError(err.message || "Đã xảy ra lỗi khi tải danh sách học phần có sẵn.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleRegister = async (maLopHocPhan: number) => {
    if (confirm("Bạn có chắc chắn muốn đăng ký lớp học phần này?")) {
      setProcessingId(maLopHocPhan)
      try {
        const success = await StudentService.registerClass(maLopHocPhan)
        if (success) {
          alert("Đăng ký lớp học phần thành công!")
          const updatedClasses = await StudentService.getAvailableClasses()
          setClasses(updatedClasses)
        } else {
          alert("Đăng ký thất bại. Vui lòng thử lại!")
        }
      } catch (err: any) {
        alert(err.message || "Có lỗi xảy ra.")
      } finally {
        setProcessingId(null)
      }
    }
  }

  const handleCancel = async (maLopHocPhan: number) => {
    if (confirm("Bạn có chắc chắn muốn hủy đăng ký lớp học phần này? Tất cả dữ liệu điểm danh liên quan sẽ bị xóa.")) {
      setProcessingId(maLopHocPhan)
      try {
        const success = await StudentService.cancelClassRegistration(maLopHocPhan)
        if (success) {
          alert("Hủy đăng ký lớp học phần thành công!")
          const updatedClasses = await StudentService.getAvailableClasses()
          setClasses(updatedClasses)
        } else {
          alert("Hủy đăng ký thất bại. Vui lòng thử lại!")
        }
      } catch (err: any) {
        alert(err.message || "Có lỗi xảy ra.")
      } finally {
        setProcessingId(null)
      }
    }
  }

  const filteredClasses = classes.filter(cls => {
    const subjectName = cls.ten_hoc_phan || ""
    const teacherName = cls.ten_giang_vien || ""
    const term = cls.nam_hoc || ""
    
    return (
      subjectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      teacherName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      term.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })

  if (loading && classes.length === 0) {
    return (
      <AppShell
        role="student"
        user={{ name: "Đang tải", email: "", avatar: "" }}
        breadcrumb="Đăng ký học phần"
      >
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
          <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
          <p className="text-[#64748B] font-medium">Đang tải danh sách học phần...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell
      role="student"
      user={profile ? { name: profile.name, email: profile.email, avatar: "" } : { name: "Sinh viên", email: "", avatar: "" }}
      breadcrumb="Đăng ký học phần"
    >
      <div className="space-y-6 max-w-6xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-[#0F172A] flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-[#0EA5E9]" />
            Đăng ký học phần trực tuyến
          </h1>
          <p className="text-[#64748B] mt-1">Đăng ký lớp học phần cho Học kỳ 1 - Năm học 2025-2026</p>
        </div>

        {/* Info & Search */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-2 border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold">Tìm kiếm học phần</CardTitle>
              <CardDescription>Nhập tên môn học, giảng viên phụ trách hoặc năm học để lọc</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
                <Input
                  placeholder="Ví dụ: Cơ sở dữ liệu, Nguyễn Văn, 2025..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 focus-visible:ring-[#0EA5E9]"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#E2E8F0] shadow-sm bg-[#F8FAFC]">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold text-[#0A2540]">Thông tin chung</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2 text-[#475569]">
              <div className="flex justify-between">
                <span>Học kỳ đăng ký:</span>
                <span className="font-semibold text-[#0F172A]">Học kỳ 1</span>
              </div>
              <div className="flex justify-between">
                <span>Năm học:</span>
                <span className="font-semibold text-[#0F172A]">2025-2026</span>
              </div>
              <div className="flex justify-between">
                <span>Lớp đã đăng ký:</span>
                <span className="font-bold text-[#166534] bg-[#DCFCE7] px-2 py-0.5 rounded-full text-xs">
                  {classes.filter(c => c.is_registered).length} lớp
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Classes Table */}
        <Card className="border-[#E2E8F0] shadow-sm overflow-hidden">
          <CardContent className="p-0">
            {filteredClasses.length > 0 ? (
              <Table>
                <TableHeader className="bg-[#F8FAFC]">
                  <TableRow>
                    <TableHead className="w-[80px]">Mã Lớp</TableHead>
                    <TableHead>Tên Môn Học</TableHead>
                    <TableHead>Số Tín Chỉ</TableHead>
                    <TableHead>Giảng Viên</TableHead>
                    <TableHead>Học Kỳ / Năm</TableHead>
                    <TableHead>Yêu Cầu</TableHead>
                    <TableHead className="text-center w-[160px]">Hành Động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredClasses.map((cls, index) => {
                    const isProcessing = processingId === cls.ma_lop_hoc_phan
                    return (
                      <TableRow key={cls.ma_lop_hoc_phan} className={index % 2 === 0 ? "bg-white" : "bg-[#F8FAFC]"}>
                        <TableCell className="font-medium text-[#0A2540]">LHP {cls.ma_lop_hoc_phan}</TableCell>
                        <TableCell className="font-semibold text-[#0F172A]">{cls.ten_hoc_phan}</TableCell>
                        <TableCell>{cls.so_tin_chi || 3} TC</TableCell>
                        <TableCell>{cls.ten_giang_vien}</TableCell>
                        <TableCell>Kỳ {cls.hoc_ky} — {cls.nam_hoc}</TableCell>
                        <TableCell>
                          <span className="text-xs font-medium text-[#475569]">
                            {cls.ty_le_chuyen_can_toi_thieu * 100}% Chuyên cần
                          </span>
                        </TableCell>
                        <TableCell className="text-center">
                          {cls.is_registered ? (
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-2">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#DCFCE7] text-[#166534]">
                                <Check className="w-3 h-3 mr-1" />
                                Đã đăng ký
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                disabled={isProcessing}
                                onClick={() => handleCancel(cls.ma_lop_hoc_phan)}
                                className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white h-7 text-xs"
                              >
                                {isProcessing ? <Loader2 className="w-3 h-3 animate-spin" /> : "Hủy"}
                              </Button>
                            </div>
                          ) : (
                            <Button
                              size="sm"
                              disabled={isProcessing}
                              onClick={() => handleRegister(cls.ma_lop_hoc_phan)}
                              className="bg-[#0EA5E9] hover:bg-[#0284C7] text-white w-24 h-8 text-xs font-medium"
                            >
                              {isProcessing ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : "Đăng ký"}
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <AlertCircle className="w-12 h-12 text-[#64748B] mb-2" />
                <p className="text-[#64748B] font-medium text-sm">Không tìm thấy học phần nào khả dụng.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
