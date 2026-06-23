"use client"

import { useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { 
  Search,
  Camera,
  RefreshCw,
  Eye,
  User,
  Check,
  X,
  Upload,
  AlertTriangle
} from "lucide-react"

import { AdminService } from "@/services/admin.service"

const mockUser = {
  name: "Admin System",
  email: "admin@university.edu.vn",
  avatar: ""
}

type FaceStatus = "approved" | "pending" | "none" | "poor"

interface StudentFace {
  id: string
  name: string
  studentId: string
  status: FaceStatus
  quality?: number
  lastUpdated?: string
  className?: string
  imageUrl?: string
}

const initialStudentFaces: StudentFace[] = [
  { id: "1", name: "Nguyễn Văn A", studentId: "SV001", status: "approved", quality: 94, lastUpdated: "20/05/2026", className: "CS101" },
  { id: "2", name: "Trần Thị B", studentId: "SV002", status: "pending", quality: 88, lastUpdated: "25/05/2026", className: "CS101" },
  { id: "3", name: "Lê Văn C", studentId: "SV003", status: "approved", quality: 91, lastUpdated: "18/05/2026", className: "CS201" },
  { id: "4", name: "Phạm Thị D", studentId: "SV004", status: "poor", quality: 45, lastUpdated: "22/05/2026", className: "CS101" },
  { id: "5", name: "Hoàng Văn E", studentId: "SV005", status: "pending", quality: 85, lastUpdated: "24/05/2026", className: "CS201" },
  { id: "6", name: "Đỗ Thị F", studentId: "SV006", status: "none", className: "CS301" },
  { id: "7", name: "Vũ Văn G", studentId: "SV007", status: "approved", quality: 97, lastUpdated: "15/05/2026", className: "CS101" },
  { id: "8", name: "Bùi Thị H", studentId: "SV008", status: "pending", quality: 82, lastUpdated: "26/05/2026", className: "CS201" },
  { id: "9", name: "Ngô Văn I", studentId: "SV009", status: "poor", quality: 52, lastUpdated: "21/05/2026", className: "CS301" },
]

const statusConfig: Record<FaceStatus, { label: string; bgClass: string; textClass: string }> = {
  approved: { label: "Đã duyệt", bgClass: "bg-[#DCFCE7]", textClass: "text-[#166534]" },
  pending: { label: "Chờ duyệt", bgClass: "bg-[#FEF9C3]", textClass: "text-[#92400E]" },
  none: { label: "Chưa đăng ký", bgClass: "bg-[#FEE2E2]", textClass: "text-[#991B1B]" },
  poor: { label: "Chất lượng kém", bgClass: "bg-[#FEF9C3]", textClass: "text-[#92400E]" },
}

export default function AdminFaceManagement() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [selectedStudent, setSelectedStudent] = useState<StudentFace | null>(null)
  const [adminNotes, setAdminNotes] = useState("")
  const [students, setStudents] = useState<StudentFace[]>(initialStudentFaces)
  const [isUploading, setIsUploading] = useState(false)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !selectedStudent) return
    const file = e.target.files[0]
    
    setIsUploading(true)
    try {
      const studentDbId = parseInt(selectedStudent.id) // Ensure this aligns with backend DB ID
      await AdminService.registerFace(studentDbId, file)
      
      const newImageUrl = URL.createObjectURL(file)
      
      alert("Đăng ký khuôn mặt thành công!")
      
      const updatedStudents = students.map(s => 
        s.id === selectedStudent.id 
          ? { ...s, status: "approved" as FaceStatus, quality: 98, lastUpdated: new Date().toLocaleDateString("vi-VN"), imageUrl: newImageUrl } 
          : s
      )
      setStudents(updatedStudents)
      setSelectedStudent(updatedStudents.find(s => s.id === selectedStudent.id) || null)
    } catch (err: any) {
      alert("Có lỗi xảy ra: " + (err.response?.data?.detail || err.message))
    } finally {
      setIsUploading(false)
    }
  }

  const filteredStudents = students.filter((student) => {
    if (statusFilter !== "all" && student.status !== statusFilter) return false
    if (searchTerm && !student.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !student.studentId.toLowerCase().includes(searchTerm.toLowerCase())) return false
    return true
  })

  return (
    <AppShell 
      role="admin" 
      user={mockUser} 
      breadcrumb="Quản lý dữ liệu khuôn mặt"
    >
      <div className="flex gap-6">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">
              Quản lý dữ liệu khuôn mặt
            </h1>
          </div>

          {/* Filters */}
          <Card className="border-[#E2E8F0] shadow-sm">
            <CardContent className="pt-6">
              <div className="flex flex-wrap gap-4">
                <div className="relative flex-1 min-w-[250px]">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
                  <Input
                    placeholder="Tìm sinh viên theo mã, tên..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Trạng thái" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tất cả</SelectItem>
                    <SelectItem value="approved">Đã duyệt</SelectItem>
                    <SelectItem value="pending">Chờ duyệt</SelectItem>
                    <SelectItem value="none">Chưa đăng ký</SelectItem>
                    <SelectItem value="poor">Chất lượng kém</SelectItem>
                  </SelectContent>
                </Select>

                <Button variant="outline">
                  <Camera className="w-4 h-4 mr-2" />
                  Thu thập hàng loạt
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Student Grid */}
          <div className="grid grid-cols-3 gap-4">
            {filteredStudents.map((student) => (
              <Card 
                key={student.id}
                className={cn(
                  "border-[#E2E8F0] shadow-sm cursor-pointer transition-all hover:shadow-md",
                  selectedStudent?.id === student.id && "ring-2 ring-[#0EA5E9]"
                )}
                onClick={() => setSelectedStudent(student)}
              >
                <CardContent className="pt-6">
                  {/* Avatar / Face Photo */}
                  <div className="relative w-24 h-24 mx-auto mb-4 rounded-lg overflow-hidden bg-[#F8FAFC]">
                    {student.status !== "none" ? (
                      student.imageUrl ? (
                        <img src={student.imageUrl} alt={student.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1A3A5C] to-[#0A2540]">
                          <User className="w-12 h-12 text-white/50" />
                        </div>
                      )
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-[#E2E8F0]">
                        <User className="w-12 h-12 text-[#64748B]" />
                      </div>
                    )}
                  </div>

                  {/* Info */}
                  <div className="text-center mb-4">
                    <p className="font-semibold text-[#0F172A]">{student.name}</p>
                    <p className="text-sm text-[#64748B]">{student.studentId}</p>
                  </div>

                  {/* Status Badge */}
                  <div className="flex justify-center mb-4">
                    <span className={cn(
                      "inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium",
                      statusConfig[student.status].bgClass,
                      statusConfig[student.status].textClass
                    )}>
                      {student.status === "approved" && <Check className="w-3 h-3" />}
                      {student.status === "pending" && <span className="w-2 h-2 rounded-full bg-current animate-pulse" />}
                      {student.status === "none" && <X className="w-3 h-3" />}
                      {student.status === "poor" && <AlertTriangle className="w-3 h-3" />}
                      {statusConfig[student.status].label}
                    </span>
                  </div>

                  {/* Embedding Vector Visualization */}
                  {student.status !== "none" && (
                    <div className="flex items-end justify-center gap-1 h-8 mb-4">
                      {[...Array(8)].map((_, i) => (
                        <div
                          key={i}
                          className="w-2 bg-gradient-to-t from-[#0A2540] to-[#0EA5E9] rounded-sm"
                          style={{ 
                            height: `${30 + ((i * 17) % 70)}%`, 
                            opacity: 0.4 + ((i * 11) % 60) / 100 
                          }}
                        />
                      ))}
                    </div>
                  )}

                  {/* Last Updated */}
                  {student.lastUpdated && (
                    <p className="text-xs text-center text-[#64748B]">
                      Cập nhật: {student.lastUpdated}
                    </p>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 mt-4">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedStudent(student)
                      }}
                    >
                      <RefreshCw className="w-4 h-4 mr-1" />
                      Cập nhật
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedStudent(student)
                      }}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Chi tiết
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Detail Drawer */}
        {selectedStudent && (
          <div className="w-[400px] bg-white border border-[#E2E8F0] rounded-lg shadow-lg overflow-hidden">
            <div className="p-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-[#0F172A]">{selectedStudent.name}</p>
                  <p className="text-sm text-[#64748B]">{selectedStudent.studentId} • {selectedStudent.className}</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => setSelectedStudent(null)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </div>

            <div className="p-4 space-y-6">
              {/* Side-by-side comparison */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-[#64748B] mb-2">Ảnh đăng ký gốc</p>
                  <div className="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-[#1A3A5C] to-[#0A2540] flex items-center justify-center">
                    {selectedStudent.imageUrl ? (
                      <img src={selectedStudent.imageUrl} alt="Gốc" className="w-full h-full object-cover" />
                    ) : (
                      <User className="w-16 h-16 text-white/50" />
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-[#64748B] mb-2">Ảnh trích xuất AI</p>
                  <div className="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-[#0A2540] to-[#1A3A5C] flex items-center justify-center">
                    {selectedStudent.imageUrl ? (
                      <img src={selectedStudent.imageUrl} alt="AI" className="w-full h-full object-cover" />
                    ) : (
                      <User className="w-16 h-16 text-white/50" />
                    )}
                  </div>
                </div>
              </div>

              {/* Quality Metrics */}
              {selectedStudent.quality && (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-[#0F172A]">Chất lượng ảnh</p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#64748B]">Độ sắc nét:</span>
                      <span className={cn(
                        "font-medium",
                        selectedStudent.quality >= 80 ? "text-[#22C55E]" :
                        selectedStudent.quality >= 60 ? "text-[#F59E0B]" : "text-[#EF4444]"
                      )}>
                        {selectedStudent.quality}/100
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#64748B]">Ánh sáng:</span>
                      <span className={cn(
                        "font-medium",
                        selectedStudent.quality >= 70 ? "text-[#22C55E]" : "text-[#F59E0B]"
                      )}>
                        {selectedStudent.quality >= 70 ? "Đạt" : "Yếu"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#64748B]">Góc mặt:</span>
                      <span className="font-medium text-[#22C55E]">Thẳng</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Admin Notes */}
              <div>
                <p className="text-sm font-medium text-[#0F172A] mb-2">Ghi chú của quản trị viên</p>
                <Textarea
                  placeholder="Nhập ghi chú..."
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  className="min-h-[80px]"
                />
              </div>

              {/* Upload Zone */}
              <div>
                <p className="text-sm font-medium text-[#0F172A] mb-2">Cập nhật ảnh mới</p>
                <label className={cn(
                  "flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-[#E2E8F0] rounded-lg cursor-pointer hover:bg-[#F8FAFC] transition-colors",
                  isUploading && "opacity-50 cursor-not-allowed"
                )}>
                  <Upload className="w-6 h-6 text-[#64748B] mb-1" />
                  <span className="text-xs text-[#64748B]">
                    {isUploading ? "Đang xử lý..." : "Kéo thả ảnh chân dung rõ mặt"}
                  </span>
                  <span className="text-xs text-[#94A3B8]">
                    (≥300x300px)
                  </span>
                  <input 
                    type="file" 
                    className="hidden" 
                    accept="image/*" 
                    onChange={handleFileUpload}
                    disabled={isUploading}
                  />
                </label>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-[#E2E8F0]">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => setSelectedStudent(null)}
                >
                  Hủy bỏ
                </Button>
                <Button className="flex-1 bg-[#0A2540] hover:bg-[#1A3A5C]">
                  Lưu thay đổi
                </Button>
              </div>

              {/* Approve/Reject for pending */}
              {selectedStudent.status === "pending" && (
                <div className="flex gap-2">
                  <Button className="flex-1 bg-[#22C55E] hover:bg-[#22C55E]/80 text-white">
                    <Check className="w-4 h-4 mr-2" />
                    Duyệt
                  </Button>
                  <Button className="flex-1 bg-[#EF4444] hover:bg-[#EF4444]/80 text-white">
                    <X className="w-4 h-4 mr-2" />
                    Từ chối
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
