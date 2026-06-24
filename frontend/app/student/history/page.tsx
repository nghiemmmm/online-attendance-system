"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { StatusBadge } from "@/components/status-badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { 
  CalendarCheck, 
  AlertTriangle, 
  TrendingUp,
  Search,
  Download,
  Upload,
  X,
  Clock,
  FileText,
  Loader2
} from "lucide-react"
import { cn } from "@/lib/utils"
import { StudentService } from "@/services/student.service"
import { StudentProfile } from "@/types/student"

type AttendanceStatus = "present" | "late" | "absent"

const methodLabels = {
  face: { label: "Khuôn mặt", bgClass: "bg-blue-100", textClass: "text-blue-700" },
  manual: { label: "Thủ công", bgClass: "bg-gray-100", textClass: "text-gray-700" },
  claim: { label: "Sau khiếu nại", bgClass: "bg-purple-100", textClass: "text-purple-700" }
}

export default function StudentHistory() {
  const [profile, setProfile] = useState<StudentProfile | null>(null)
  const [attendance, setAttendance] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [subjectFilter, setSubjectFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [claimModalOpen, setClaimModalOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null)
  const [claimReason, setClaimReason] = useState("")
  const [claimFile, setClaimFile] = useState<File | null>(null)
  const [submittingClaim, setSubmittingClaim] = useState(false)

  const loadData = async () => {
    try {
      setLoading(true)
      const [profileData, attendanceData] = await Promise.all([
        StudentService.getProfile(),
        StudentService.getAttendance()
      ])
      setProfile(profileData)
      setAttendance(attendanceData)
    } catch (err: any) {
      console.error("Error loading history:", err)
      setError(err.message || "Đã xảy ra lỗi khi tải lịch sử điểm danh.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Calculate unique subjects list for filter dropdown
  const uniqueSubjects = Array.from(new Set(attendance.map(a => a.ten_hoc_phan || `Lớp ${a.ma_lop_hoc_phan}`)))

  // Calculate statistics
  const totalSessions = attendance.length
  const presentCount = attendance.filter(a => a.trang_thai === "CO_MAT").length
  const lateCount = attendance.filter(a => a.trang_thai === "DI_MUON").length
  const absentCount = attendance.filter(a => a.trang_thai === "VANG").length
  const attendedCount = presentCount + lateCount
  const attendanceRate = totalSessions > 0 ? ((attendedCount / totalSessions) * 100).toFixed(1) : "0.0"

  // Group absences by class for warning counts
  const absencesByClass: Record<number, { absent: number, total: number }> = {}
  attendance.forEach(a => {
    const classId = a.ma_lop_hoc_phan
    if (!absencesByClass[classId]) {
      absencesByClass[classId] = { absent: 0, total: 0 }
    }
    absencesByClass[classId].total++
    if (a.trang_thai === "VANG") {
      absencesByClass[classId].absent++
    }
  })
  const warningCount = Object.values(absencesByClass).filter(c => c.absent / c.total >= 0.2).length

  // Filter records
  const filteredData = attendance.filter((a) => {
    const subjectName = a.ten_hoc_phan || `Lớp ${a.ma_lop_hoc_phan}`
    const mappedStatus = a.trang_thai === "CO_MAT" ? "present" : a.trang_thai === "DI_MUON" ? "late" : "absent"
    
    if (subjectFilter !== "all" && subjectName !== subjectFilter) return false
    if (statusFilter !== "all" && mappedStatus !== statusFilter) return false
    if (searchTerm && !subjectName.toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  // Format attendance list for rendering
  const mappedRecords = filteredData.map((item, idx) => {
    const isAbsent = item.trang_thai === "VANG"
    const isLate = item.trang_thai === "DI_MUON"
    const mappedStatus = item.trang_thai === "CO_MAT" ? "present" as const : isLate ? "late" as const : "absent" as const
    return {
      id: item.ma_diem_danh || idx,
      subject: item.ten_hoc_phan || `Lớp học phần ${item.ma_lop_hoc_phan}`,
      date: item.ngay_hoc ? new Date(item.ngay_hoc).toLocaleDateString("vi-VN") : "N/A",
      session: item.ma_lop_hoc_phan,
      status: mappedStatus,
      lateMinutes: isLate ? 10 : 0,
      method: "face" as const,
      canClaim: isAbsent || isLate,
      raw: item
    }
  })

  // Streak days
  const streakDays = attendance.slice(-10).map((item) => ({
    date: item.ngay_hoc ? item.ngay_hoc.substring(5, 10).replace("-", "/") : "N/A",
    status: item.trang_thai === "CO_MAT" ? "present" : item.trang_thai === "DI_MUON" ? "late" : "absent"
  }))

  const handleClaimClick = (record: any) => {
    setSelectedRecord(record)
    setClaimModalOpen(true)
  }

  const handleClaimSubmit = async () => {
    if (!selectedRecord) return
    setSubmittingClaim(true)
    try {
      await StudentService.submitClaim({
        reason: claimReason,
        ma_diem_danh: selectedRecord.id,
        subjectCode: selectedRecord.raw.ma_lop_hoc_phan,
        subjectName: selectedRecord.subject,
        sessionNumber: selectedRecord.session,
        currentStatus: selectedRecord.status
      })
      alert("Đã gửi khiếu nại thành công!")
      setClaimModalOpen(false)
      setClaimReason("")
      setClaimFile(null)
      setSelectedRecord(null)
      loadData() // Refresh list
    } catch (err: any) {
      alert(err.message || "Đã xảy ra lỗi khi gửi khiếu nại.")
    } finally {
      setSubmittingClaim(false)
    }
  }

  if (loading) {
    return (
      <AppShell 
        role="student" 
        user={{ name: "Đang tải", email: "", avatar: "" }} 
        breadcrumb="Lịch sử điểm danh"
      >
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
          <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
          <p className="text-[#64748B] font-medium">Đang tải lịch sử điểm danh...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell 
      role="student" 
      user={profile ? { name: profile.name, email: profile.email, avatar: "" } : { name: "Sinh viên", email: "", avatar: "" }} 
      breadcrumb="Lịch sử điểm danh"
      notificationCount={warningCount}
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Lịch sử điểm danh</h1>
            <span className="inline-flex items-center px-2.5 py-1 mt-2 rounded-full text-xs font-medium bg-[#DBEAFE] text-[#1E40AF]">
              HK1-2025-2026
            </span>
          </div>
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
                  <p className="text-3xl font-bold text-[#22C55E] mt-1">{attendedCount}/{totalSessions}</p>
                  <p className="text-xs text-[#64748B] mt-1">Số buổi có mặt + đi muộn</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#DBEAFE] flex items-center justify-center">
                  <CalendarCheck className="w-6 h-6 text-[#3B82F6]" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-[#64748B]">Cảnh báo vắng</p>
                  <p className="text-3xl font-bold text-[#F59E0B] mt-1">{warningCount} môn</p>
                  <p className="text-xs text-[#F59E0B] mt-1">Vượt quá 20% giới hạn vắng</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-[#FEF9C3] flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-[#F59E0B]" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-4">
              <Select value={subjectFilter} onValueChange={setSubjectFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Tất cả môn học" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tất cả môn học</SelectItem>
                  {uniqueSubjects.map(subj => (
                    <SelectItem key={subj} value={subj}>{subj}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="flex bg-[#F1F5F9] rounded-lg p-1">
                {["all", "present", "late", "absent"].map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={cn(
                      "px-4 py-2 rounded-md text-sm font-medium transition-all",
                      statusFilter === status
                        ? "bg-white text-[#0A2540] shadow-sm"
                        : "text-[#64748B] hover:text-[#0F172A]"
                    )}
                  >
                    {status === "all" ? "Tất cả" : status === "present" ? "Có mặt" : status === "late" ? "Muộn" : "Vắng"}
                  </button>
                ))}
              </div>

              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
                <Input
                  placeholder="Tìm theo môn học..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Attendance Streak */}
        {streakDays.length > 0 && (
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-[#0F172A]">
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

        {/* Data Table */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardContent className="pt-6">
            {mappedRecords.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]">STT</TableHead>
                    <TableHead>Môn học</TableHead>
                    <TableHead>Ngày học</TableHead>
                    <TableHead>Lớp học phần</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Phút muộn</TableHead>
                    <TableHead>Phương thức</TableHead>
                    <TableHead>Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mappedRecords.map((record, index) => (
                    <TableRow key={record.id} className={index % 2 === 0 ? "bg-[#F8FAFC]" : ""}>
                      <TableCell className="font-medium">{index + 1}</TableCell>
                      <TableCell className="font-medium">{record.subject}</TableCell>
                      <TableCell>{record.date}</TableCell>
                      <TableCell>Mã: {record.session}</TableCell>
                      <TableCell>
                        <StatusBadge status={record.status} />
                      </TableCell>
                      <TableCell>
                        {record.lateMinutes > 0 ? (
                          <span className="text-[#F59E0B]">{record.lateMinutes} phút</span>
                        ) : (
                          <span className="text-[#64748B]">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <span className={cn(
                          "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
                          methodLabels[record.method].bgClass,
                          methodLabels[record.method].textClass
                        )}>
                          {methodLabels[record.method].label}
                        </span>
                      </TableCell>
                      <TableCell>
                        {record.canClaim ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleClaimClick(record)}
                            className="text-[#0EA5E9] hover:text-[#0A2540] hover:bg-[#EFF6FF]"
                          >
                            <FileText className="w-4 h-4 mr-1" />
                            Gửi khiếu nại
                          </Button>
                        ) : (
                          <span className="text-xs text-[#64748B]">-</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-sm text-[#64748B] text-center py-12">Không tìm thấy bản ghi điểm danh nào khớp bộ lọc.</p>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E2E8F0]">
              <p className="text-sm text-[#64748B]">
                Hiển thị {mappedRecords.length} / {attendance.length} bản ghi
              </p>
              <Button variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Xuất Excel
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Claim Modal */}
      <Dialog open={claimModalOpen} onOpenChange={setClaimModalOpen}>
        <DialogContent className="max-w-[560px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Gửi khiếu nại điểm danh
            </DialogTitle>
          </DialogHeader>

          {selectedRecord && (
            <div className="space-y-4">
              {/* Pre-filled Info */}
              <div className="p-4 bg-[#F8FAFC] rounded-lg space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-[#64748B]">Môn học:</span>
                  <span className="text-sm font-medium text-[#0F172A]">{selectedRecord.subject}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#64748B]">Lớp học phần:</span>
                  <span className="text-sm font-medium text-[#0F172A]">
                    Mã LHP: {selectedRecord.session} — {selectedRecord.date}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-[#64748B]">Trạng thái hiện tại:</span>
                  <StatusBadge status={selectedRecord.status} />
                </div>
              </div>

              {/* Reason */}
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">
                  Lý do khiếu nại <span className="text-red-500">*</span>
                </label>
                <Textarea
                  placeholder="Mô tả chi tiết lý do bạn bị ghi nhận sai..."
                  value={claimReason}
                  onChange={(e) => setClaimReason(e.target.value)}
                  className="min-h-[120px]"
                  maxLength={500}
                />
                <p className="text-xs text-[#64748B] text-right mt-1">
                  {claimReason.length}/500 ký tự
                </p>
              </div>

              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">
                  Bằng chứng đính kèm
                </label>
                {!claimFile ? (
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-[#0EA5E9] rounded-lg cursor-pointer hover:bg-[#EFF6FF] transition-colors">
                    <Upload className="w-8 h-8 text-[#0EA5E9] mb-2" />
                    <span className="text-sm text-[#64748B]">
                      Kéo thả file vào đây hoặc nhấn để chọn
                    </span>
                    <span className="text-xs text-[#64748B] mt-1">
                      JPG, PNG, PDF — tối đa 5MB
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept=".jpg,.jpeg,.png,.pdf"
                      onChange={(e) => setClaimFile(e.target.files?.[0] || null)}
                    />
                  </label>
                ) : (
                  <div className="flex items-center gap-3 p-3 bg-[#F8FAFC] rounded-lg">
                    <FileText className="w-8 h-8 text-[#0EA5E9]" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-[#0F172A]">{claimFile.name}</p>
                      <p className="text-xs text-[#64748B]">
                        {(claimFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setClaimFile(null)}
                      className="text-[#64748B] hover:text-[#EF4444]"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" disabled={submittingClaim} onClick={() => setClaimModalOpen(false)}>
              Hủy
            </Button>
            <Button
              onClick={handleClaimSubmit}
              disabled={!claimReason.trim() || submittingClaim}
              className="bg-[#0A2540] hover:bg-[#1A3A5C]"
            >
              {submittingClaim && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
              Gửi khiếu nại
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  )
}
