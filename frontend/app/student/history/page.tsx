"use client"

import { useState } from "react"
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
  FileText
} from "lucide-react"
import { cn } from "@/lib/utils"

const mockUser = {
  name: "Nguyễn Văn An",
  email: "an.nguyen@student.edu.vn",
  avatar: ""
}

type AttendanceStatus = "present" | "late" | "absent"

interface AttendanceRecord {
  id: number
  subject: string
  date: string
  session: number
  status: AttendanceStatus
  lateMinutes: number
  method: "face" | "manual" | "claim"
  canClaim: boolean
}

const attendanceData: AttendanceRecord[] = [
  { id: 1, subject: "Lập trình Web", date: "25/05/2026", session: 7, status: "present", lateMinutes: 0, method: "face", canClaim: false },
  { id: 2, subject: "Cơ sở dữ liệu", date: "24/05/2026", session: 5, status: "present", lateMinutes: 0, method: "face", canClaim: false },
  { id: 3, subject: "Mạng máy tính", date: "23/05/2026", session: 3, status: "late", lateMinutes: 8, method: "face", canClaim: true },
  { id: 4, subject: "Lập trình Web", date: "22/05/2026", session: 6, status: "present", lateMinutes: 0, method: "face", canClaim: false },
  { id: 5, subject: "Trí tuệ nhân tạo", date: "21/05/2026", session: 4, status: "absent", lateMinutes: 0, method: "manual", canClaim: true },
  { id: 6, subject: "Cơ sở dữ liệu", date: "20/05/2026", session: 4, status: "present", lateMinutes: 0, method: "face", canClaim: false },
  { id: 7, subject: "Mạng máy tính", date: "19/05/2026", session: 2, status: "present", lateMinutes: 0, method: "claim", canClaim: false },
  { id: 8, subject: "Lập trình Web", date: "18/05/2026", session: 5, status: "late", lateMinutes: 12, method: "face", canClaim: false },
]

const methodLabels = {
  face: { label: "Khuôn mặt", bgClass: "bg-blue-100", textClass: "text-blue-700" },
  manual: { label: "Thủ công", bgClass: "bg-gray-100", textClass: "text-gray-700" },
  claim: { label: "Sau khiếu nại", bgClass: "bg-purple-100", textClass: "text-purple-700" }
}

export default function StudentHistory() {
  const [subjectFilter, setSubjectFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [claimModalOpen, setClaimModalOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<AttendanceRecord | null>(null)
  const [claimReason, setClaimReason] = useState("")
  const [claimFile, setClaimFile] = useState<File | null>(null)

  const filteredData = attendanceData.filter((record) => {
    if (subjectFilter !== "all" && record.subject !== subjectFilter) return false
    if (statusFilter !== "all" && record.status !== statusFilter) return false
    if (searchTerm && !record.subject.toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  const handleClaimClick = (record: AttendanceRecord) => {
    setSelectedRecord(record)
    setClaimModalOpen(true)
  }

  const handleClaimSubmit = () => {
    console.log("Claim submitted:", { record: selectedRecord, reason: claimReason, file: claimFile })
    setClaimModalOpen(false)
    setClaimReason("")
    setClaimFile(null)
    setSelectedRecord(null)
  }

  return (
    <AppShell 
      role="student" 
      user={mockUser} 
      breadcrumb="Lịch sử điểm danh"
      notificationCount={2}
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Lịch sử điểm danh</h1>
            <span className="inline-flex items-center px-2.5 py-1 mt-2 rounded-full text-xs font-medium bg-[#DBEAFE] text-[#1E40AF]">
              HK1-2024-2025
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
                  <p className="text-3xl font-bold text-[#0A2540] mt-1">87.5%</p>
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
                  <p className="text-sm text-[#64748B]">Tổng buổi có mặt</p>
                  <p className="text-3xl font-bold text-[#22C55E] mt-1">42/48</p>
                  <p className="text-xs text-[#64748B] mt-1">buổi</p>
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
                  <SelectItem value="Lập trình Web">Lập trình Web</SelectItem>
                  <SelectItem value="Cơ sở dữ liệu">Cơ sở dữ liệu</SelectItem>
                  <SelectItem value="Mạng máy tính">Mạng máy tính</SelectItem>
                  <SelectItem value="Trí tuệ nhân tạo">Trí tuệ nhân tạo</SelectItem>
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
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-[#0F172A]">
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

        {/* Data Table */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]">STT</TableHead>
                  <TableHead>Môn học</TableHead>
                  <TableHead>Ngày học</TableHead>
                  <TableHead>Buổi #</TableHead>
                  <TableHead>Trạng thái</TableHead>
                  <TableHead>Phút muộn</TableHead>
                  <TableHead>Phương thức</TableHead>
                  <TableHead>Hành động</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.map((record, index) => (
                  <TableRow key={record.id} className={index % 2 === 0 ? "bg-[#F8FAFC]" : ""}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell className="font-medium">{record.subject}</TableCell>
                    <TableCell>{record.date}</TableCell>
                    <TableCell>Buổi {record.session}</TableCell>
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
                      {record.canClaim && (record.status === "absent" || record.status === "late") ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleClaimClick(record)}
                          className="text-[#0EA5E9] hover:text-[#0A2540] hover:bg-[#EFF6FF]"
                        >
                          <FileText className="w-4 h-4 mr-1" />
                          Gửi khiếu nại
                        </Button>
                      ) : record.status !== "present" && !record.canClaim ? (
                        <span className="text-xs text-[#64748B]" title="Hết hạn khiếu nại">
                          Hết hạn
                        </span>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {/* Footer */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E2E8F0]">
              <p className="text-sm text-[#64748B]">
                Hiển thị {filteredData.length} / {attendanceData.length} bản ghi
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
                  <span className="text-sm text-[#64748B]">Buổi:</span>
                  <span className="text-sm font-medium text-[#0F172A]">
                    Buổi {selectedRecord.session} — {selectedRecord.date}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-[#64748B]">Trạng thái hiện tại:</span>
                  <StatusBadge status={selectedRecord.status} />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-[#64748B]">Thời hạn khiếu nại:</span>
                  <span className="text-sm font-medium text-[#F59E0B] flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Còn 23 giờ 12 phút
                  </span>
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

              {/* Notice */}
              <p className="text-xs text-[#64748B]">
                Khiếu nại chỉ được gửi 1 lần mỗi buổi học
              </p>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setClaimModalOpen(false)}>
              Hủy
            </Button>
            <Button
              onClick={handleClaimSubmit}
              disabled={!claimReason.trim()}
              className="bg-[#0A2540] hover:bg-[#1A3A5C]"
            >
              Gửi khiếu nại
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  )
}
