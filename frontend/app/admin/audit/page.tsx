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
  { value: "user_create", label: "Tạo người dùng" },
  { value: "user_update", label: "Cập nhật người dùng" },
  { value: "user_delete", label: "Xóa người dùng" },
  { value: "face_upload", label: "Tải lên khuôn mặt" },
  { value: "face_delete", label: "Xóa khuôn mặt" },
  { value: "face_verify", label: "Xác minh khuôn mặt" },
  { value: "attendance_edit", label: "Sửa điểm danh" },
  { value: "session_start", label: "Bắt đầu phiên" },
  { value: "session_end", label: "Kết thúc phiên" },
  { value: "login_success", label: "Đăng nhập" },
  { value: "login_failed", label: "Đăng nhập thất bại" },
  { value: "settings_change", label: "Thay đổi cài đặt" },
  { value: "report_export", label: "Xuất báo cáo" },
]

const getActionIcon = (action: string) => {
  switch (action) {
    case "user_create":
      return <UserPlus className="h-4 w-4" />
    case "user_update":
      return <Edit className="h-4 w-4" />
    case "user_delete":
      return <Trash2 className="h-4 w-4" />
    case "face_upload":
    case "face_delete":
    case "face_verify":
      return <Camera className="h-4 w-4" />
    case "attendance_edit":
      return <FileText className="h-4 w-4" />
    case "session_start":
    case "session_end":
      return <Clock className="h-4 w-4" />
    case "login_success":
    case "login_failed":
      return <Key className="h-4 w-4" />
    case "settings_change":
      return <Settings className="h-4 w-4" />
    case "report_export":
      return <Download className="h-4 w-4" />
    case "backup_complete":
      return <Database className="h-4 w-4" />
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
      const mapped = response.map((log: any) => ({
        id: log.id,
        timestamp: log.timestamp || "2026-06-24 12:00:00",
        user: log.user_info || { name: log.user || "Hệ thống", email: "system@university.edu.vn", avatar: null },
        action: log.action_type || log.action || "other",
        target: log.target || "",
        ip: log.ip || "127.0.0.1",
        status: log.status || "success",
        details: log.details || ""
      }))
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
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-primary/10 p-2">
                      <History className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-foreground">{logs.length}</p>
                      <p className="text-sm text-muted-foreground">Tổng hoạt động</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-success/10 p-2">
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-success">
                        {logs.filter(l => l.status === "success").length}
                      </p>
                      <p className="text-sm text-muted-foreground">Thành công</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-warning/10 p-2">
                      <AlertTriangle className="h-5 w-5 text-warning" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-warning">
                        {logs.filter(l => l.status === "warning").length}
                      </p>
                      <p className="text-sm text-muted-foreground">Cảnh báo</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-destructive/10 p-2">
                      <XCircle className="h-5 w-5 text-destructive" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-destructive">
                        {logs.filter(l => l.status === "error" || l.status === "danger").length}
                      </p>
                      <p className="text-sm text-muted-foreground">Lỗi</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card>
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
                      <SelectItem value="error">Lỗi</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Audit Log Table */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Lịch sử hoạt động</CardTitle>
                <CardDescription>
                  Hiển thị {filteredLogs.length} bản ghi
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {paginatedLogs.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Không tìm thấy bản ghi hoạt động nào phù hợp.
                    </div>
                  ) : (
                    paginatedLogs.map((log) => (
                      <div
                        key={log.id}
                        className="flex items-start gap-4 rounded-lg border border-border p-4 transition-colors hover:bg-muted/50"
                      >
                        {/* Action Icon */}
                        <div className={`rounded-full p-2 ${
                          log.status === "success" ? "bg-success/10 text-success" :
                          log.status === "warning" ? "bg-warning/10 text-warning" :
                          "bg-destructive/10 text-destructive"
                        }`}>
                          {getActionIcon(log.action)}
                        </div>

                        {/* Content */}
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-foreground">
                              {getActionLabel(log.action)}
                            </span>
                            <span className={cn(
                              "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                              log.status === "success" ? "bg-emerald-500/10 text-emerald-400" :
                              log.status === "warning" ? "bg-amber-500/10 text-amber-400" :
                              "bg-rose-500/10 text-rose-400"
                            )}>
                              {log.status === "success" ? "Thành công" :
                               log.status === "warning" ? "Cảnh báo" : "Lỗi"}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium text-foreground">{log.target}</span>
                            {" - "}
                            {log.details}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Avatar className="h-4 w-4">
                                <AvatarImage src={log.user.avatar || undefined} />
                                <AvatarFallback className="text-[8px]">
                                  {log.user.name.charAt(0)}
                                </AvatarFallback>
                              </Avatar>
                              <span>{log.user.name}</span>
                            </div>
                            <span>IP: {log.ip}</span>
                          </div>
                        </div>

                        {/* Timestamp */}
                        <div className="text-right">
                          <p className="text-sm font-medium text-foreground">
                            {log.timestamp.includes(" ") ? log.timestamp.split(" ")[1] : log.timestamp}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {log.timestamp.includes(" ") ? log.timestamp.split(" ")[0] : ""}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Pagination */}
                <div className="mt-6 flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Trang {currentPage} / {totalPages}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Trước
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages || filteredLogs.length === 0}
                    >
                      Sau
                      <ChevronRight className="h-4 w-4" />
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
