"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  History,
  Search,
  Filter,
  Download,
  RefreshCw,
  User,
  Shield,
  Settings,
  Database,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Edit,
  Trash2,
  UserPlus,
  Key,
  Camera,
  FileText,
  Clock,
  ChevronLeft,
  ChevronRight,
  Loader2
} from "lucide-react"
import { AdminService } from "@/services/admin.service"

const actionTypes = [
  { value: "all", label: "Tất cả hành động" },
  { value: "DANG_NHAP", label: "Đăng nhập" },
  { value: "DANG_KY_KHUON_MAT", label: "Đăng ký khuôn mặt" },
  { value: "XAC_MINH_KHUON_MAT", label: "Điểm danh quét mặt" },
  { value: "PHE_DUYET_KHUON_MAT", label: "Phê duyệt khuôn mặt" },
  { value: "TU_CHOI_KHUON_MAT", label: "Từ chối khuôn mặt" },
  { value: "TAO_NGUOI_DUNG", label: "Tạo người dùng" },
  { value: "CAP_NHAT_NGUOI_DUNG", label: "Cập nhật người dùng" },
  { value: "XOA_NGUOI_DUNG", label: "Xóa người dùng" },
]

const getActionIcon = (action: string) => {
  switch (action) {
    case "TAO_NGUOI_DUNG":
      return <UserPlus className="h-4 w-4" />
    case "CAP_NHAT_NGUOI_DUNG":
      return <Edit className="h-4 w-4" />
    case "XOA_NGUOI_DUNG":
      return <Trash2 className="h-4 w-4" />
    case "DANG_KY_KHUON_MAT":
      return <Camera className="h-4 w-4" />
    case "XAC_MINH_KHUON_MAT":
    case "PHE_DUYET_KHUON_MAT":
      return <CheckCircle2 className="h-4 w-4" />
    case "TU_CHOI_KHUON_MAT":
      return <XCircle className="h-4 w-4" />
    case "DANG_NHAP":
      return <Key className="h-4 w-4" />
    default:
      return <History className="h-4 w-4" />
  }
}

const getActionLabel = (action: string) => {
  const found = actionTypes.find(a => a.value === action)
  return found ? found.label : action
}

export default function AdminAuditPage() {
  const [adminUser, setAdminUser] = useState({
    name: "Admin",
    email: "admin@university.edu.vn",
    avatar: ""
  })
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedAction, setSelectedAction] = useState("all")
  const [selectedStatus, setSelectedStatus] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)

  const fetchLogs = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await AdminService.getLogs()
      const mapped = response.map((log: any) => {
        const raw = log.raw || {}
        const localTimeStr = raw.timestamp
          ? new Date(raw.timestamp).toLocaleString("vi-VN")
          : log.time || "02/07/2026, 02:44:00"
        const parts = localTimeStr.split(", ")
        const datePart = parts[0] || ""
        const timePart = parts[1] || ""

        return {
          id: log.id || raw.audit_log_id?.toString(),
          timestamp: localTimeStr,
          timePart: timePart,
          datePart: datePart,
          user: {
            name: raw.account_id ? `Tài khoản #${raw.account_id}` : "Hệ thống",
            email: raw.account_id ? `user${raw.account_id}@university.edu.vn` : "system@university.edu.vn",
            avatar: null
          },
          action: raw.action || "Hoạt động",
          target: raw.target_id ? `${raw.target_type || "Đối tượng"} #${raw.target_id}` : raw.target_type || "",
          ip: raw.ip_address || "127.0.0.1",
          status: raw.status?.toLowerCase() === "failed" || raw.status === "FAILED" ? "error" : "success",
          details: raw.detail || ""
        }
      })
      setLogs(mapped)
    } catch (err: any) {
      console.error(err)
      setError("Không thể tải nhật ký hoạt động từ máy chủ.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    AdminService.getProfile()
      .then(p => setAdminUser({ ...p, avatar: "" }))
      .catch(err => console.error("Lỗi tải profile admin:", err))
    fetchLogs()
  }, [])

  const filteredLogs = logs.filter(log => {
    const matchesSearch =
      log.user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.target.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.details.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesAction = selectedAction === "all" || log.action === selectedAction
    const matchesStatus = selectedStatus === "all" || log.status === selectedStatus
    return matchesSearch && matchesAction && matchesStatus
  })

  const itemsPerPage = 8
  const totalPages = Math.max(1, Math.ceil(filteredLogs.length / itemsPerPage))
  const paginatedLogs = filteredLogs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  return (
    <AppShell role="admin" user={adminUser} breadcrumb="Nhật ký hoạt động">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Nhật ký hoạt động</h1>
            <p className="text-sm text-muted-foreground">
              Theo dõi tất cả hoạt động trong hệ thống
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={fetchLogs} disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Làm mới
            </Button>
            <Button size="sm" className="bg-primary text-primary-foreground">
              <Download className="mr-2 h-4 w-4" />
              Xuất log
            </Button>
          </div>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0] shadow-sm">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải nhật ký hoạt động...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle className="w-12 h-12 text-[#EF4444] mb-3" />
              <h3 className="text-lg font-semibold text-[#991B1B] mb-1">Đã xảy ra lỗi</h3>
              <p className="text-[#DC2626] mb-4 max-w-md text-sm">{error}</p>
              <Button onClick={fetchLogs} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && (
          <>
            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-all duration-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-slate-100 p-2.5">
                      <History className="h-5 w-5 text-slate-600" />
                    </div>
                    <div>
                      <p className="text-3xl font-extrabold text-[#0F172A]">{logs.length}</p>
                      <p className="text-sm font-semibold text-[#0F172A]/80 mt-0.5">Tổng số hoạt động</p>
                      <p className="text-xs text-[#64748B] mt-1">Ghi nhận mọi tương tác trong hệ thống</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-all duration-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-[#E8F5E9] p-2.5">
                      <CheckCircle2 className="h-5 w-5 text-[#22C55E]" />
                    </div>
                    <div>
                      <p className="text-3xl font-extrabold text-[#22C55E]">
                        {logs.filter(l => l.status === "success" || l.status === "SUCCESS").length}
                      </p>
                      <p className="text-sm font-semibold text-[#22C55E] mt-0.5">Tác vụ thành công</p>
                      <p className="text-xs text-[#64748B] mt-1">Các hành động hoàn thành hợp lệ</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-all duration-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-[#FFF3E0] p-2.5">
                      <AlertTriangle className="h-5 w-5 text-[#F59E0B]" />
                    </div>
                    <div>
                      <p className="text-3xl font-extrabold text-[#F59E0B]">
                        {logs.filter(l => l.status === "warning" || l.status === "WARNING").length}
                      </p>
                      <p className="text-sm font-semibold text-[#F59E0B] mt-0.5">Cảnh báo hệ thống</p>
                      <p className="text-xs text-[#64748B] mt-1">Các trường hợp cần QTV lưu ý</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-all duration-200">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-[#FFEBEE] p-2.5">
                      <XCircle className="h-5 w-5 text-[#EF4444]" />
                    </div>
                    <div>
                      <p className="text-3xl font-extrabold text-[#EF4444]">
                        {logs.filter(l => l.status === "error" || l.status === "danger" || l.status === "FAILED" || l.status === "failed").length}
                      </p>
                      <p className="text-sm font-semibold text-[#EF4444] mt-0.5">Tác vụ thất bại</p>
                      <p className="text-xs text-[#64748B] mt-1">Các lỗi xảy ra hoặc đăng nhập sai</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card className="border-[#E2E8F0] shadow-sm">
              <CardContent className="pt-6">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Tìm kiếm theo người dùng, mục tiêu, chi tiết..."
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value)
                        setCurrentPage(1)
                      }}
                      className="pl-9"
                    />
                  </div>
                  <Select value={selectedAction} onValueChange={(val) => {
                    setSelectedAction(val)
                    setCurrentPage(1)
                  }}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Loại hành động" />
                    </SelectTrigger>
                    <SelectContent>
                      {actionTypes.map(action => (
                        <SelectItem key={action.value} value={action.value}>
                          {action.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select value={selectedStatus} onValueChange={(val) => {
                    setSelectedStatus(val)
                    setCurrentPage(1)
                  }}>
                    <SelectTrigger className="w-[140px]">
                      <SelectValue placeholder="Trạng thái" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tất cả</SelectItem>
                      <SelectItem value="success">Thành công</SelectItem>
                      <SelectItem value="warning">Cảnh báo</SelectItem>
                      <SelectItem value="error">Thất bại</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Audit Log Table */}
            <Card className="border-[#E2E8F0] shadow-sm">
              <CardHeader>
                <CardTitle className="text-base text-[#0F172A]">Lịch sử hoạt động</CardTitle>
                <CardDescription>
                  Hiển thị {filteredLogs.length} bản ghi
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {paginatedLogs.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Không tìm thấy bản ghi hoạt động nào phù hợp.
                    </div>
                  ) : (
                    paginatedLogs.map((log) => (
                      <div
                        key={log.id}
                        className="flex items-start gap-4 rounded-xl border border-[#E2E8F0] p-4 transition-all hover:bg-slate-50 hover:shadow-sm"
                      >
                        {/* Action Icon */}
                        <div className={`rounded-full p-2.5 ${
                          log.status === "success" ? "bg-[#E8F5E9] text-[#22C55E]" :
                          log.status === "warning" ? "bg-[#FFF3E0] text-[#F59E0B]" :
                          "bg-[#FFEBEE] text-[#EF4444]"
                        }`}>
                          {getActionIcon(log.action)}
                        </div>

                        {/* Content */}
                        <div className="flex-1 space-y-1.5">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-sm text-[#0F172A]">
                              {getActionLabel(log.action)}
                            </span>
                            <span className={cn(
                              "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border",
                              log.status === "success" ? "bg-[#E8F5E9] text-[#22C55E] border-[#22C55E]/15" :
                              log.status === "warning" ? "bg-[#FFF3E0] text-[#F59E0B] border-[#F59E0B]/15" :
                              "bg-[#FFEBEE] text-[#EF4444] border-[#EF4444]/15"
                            )}>
                              {log.status === "success" ? "Thành công" :
                               log.status === "warning" ? "Cảnh báo" : "Thất bại"}
                            </span>
                          </div>
                          <p className="text-sm text-[#64748B]">
                            {log.target && <span className="font-semibold text-[#0F172A]">{log.target}</span>}
                            {log.target && log.details && " — "}
                            {log.details}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-[#94A3B8]">
                            <div className="flex items-center gap-1.5">
                              <Avatar className="h-5 w-5 border border-slate-200">
                                <AvatarImage src={log.user.avatar || undefined} />
                                <AvatarFallback className="text-[9px] bg-slate-100 font-bold text-slate-600">
                                  {log.user.name.charAt(0)}
                                </AvatarFallback>
                              </Avatar>
                              <span className="font-medium text-[#64748B]">{log.user.name}</span>
                            </div>
                            <span>IP: {log.ip}</span>
                          </div>
                        </div>

                        {/* Timestamp */}
                        <div className="text-right flex flex-col justify-center min-w-[90px]">
                          <p className="text-sm font-semibold text-[#0F172A]">
                            {log.timePart}
                          </p>
                          <p className="text-xs text-[#64748B] mt-0.5">
                            {log.datePart}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Pagination */}
                <div className="mt-6 flex items-center justify-between border-t border-[#E2E8F0] pt-4">
                  <p className="text-sm text-[#64748B]">
                    Trang <span className="font-semibold text-[#0F172A]">{currentPage}</span> / <span className="font-semibold text-[#0F172A]">{totalPages}</span>
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="border-[#E2E8F0] text-slate-600"
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Trước
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages || filteredLogs.length === 0}
                      className="border-[#E2E8F0] text-slate-600"
                    >
                      Sau
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
    </AppShell>
  )
}
