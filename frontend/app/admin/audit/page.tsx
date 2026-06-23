"use client"

import { useState } from "react"
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
import { StatusBadge } from "@/components/status-badge"
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
  ChevronRight
} from "lucide-react"

// Mock data for audit logs
const auditLogs = [
  {
    id: "LOG001",
    timestamp: "2024-01-15 14:32:15",
    user: { name: "Admin Nguyen", email: "admin@university.edu.vn", avatar: null },
    action: "user_create",
    target: "Tran Van Minh (SV2024001)",
    ip: "192.168.1.100",
    status: "success",
    details: "Tao tai khoan sinh vien moi"
  },
  {
    id: "LOG002",
    timestamp: "2024-01-15 14:28:42",
    user: { name: "GV. Le Thi Hoa", email: "lehoa@university.edu.vn", avatar: null },
    action: "attendance_edit",
    target: "Buoi hoc CS101-15/01/2024",
    ip: "192.168.1.105",
    status: "success",
    details: "Chinh sua diem danh cho 3 sinh vien"
  },
  {
    id: "LOG003",
    timestamp: "2024-01-15 14:15:30",
    user: { name: "System", email: "system@university.edu.vn", avatar: null },
    action: "face_verify",
    target: "Nguyen Thi Mai (SV2023045)",
    ip: "10.0.0.1",
    status: "warning",
    details: "Do tin cay thap: 78.5%"
  },
  {
    id: "LOG004",
    timestamp: "2024-01-15 14:10:22",
    user: { name: "Admin Tran", email: "admin2@university.edu.vn", avatar: null },
    action: "face_delete",
    target: "Du lieu khuon mat SV2022089",
    ip: "192.168.1.101",
    status: "success",
    details: "Xoa du lieu khuon mat theo yeu cau"
  },
  {
    id: "LOG005",
    timestamp: "2024-01-15 13:55:18",
    user: { name: "GV. Pham Van Duc", email: "phamduc@university.edu.vn", avatar: null },
    action: "session_start",
    target: "Lop CNTT-K65A - Lap trinh Web",
    ip: "192.168.1.110",
    status: "success",
    details: "Bat dau phien diem danh"
  },
  {
    id: "LOG006",
    timestamp: "2024-01-15 13:45:00",
    user: { name: "System", email: "system@university.edu.vn", avatar: null },
    action: "login_failed",
    target: "admin@university.edu.vn",
    ip: "203.162.45.67",
    status: "error",
    details: "Dang nhap that bai - Sai mat khau (lan 3)"
  },
  {
    id: "LOG007",
    timestamp: "2024-01-15 13:30:45",
    user: { name: "Admin Nguyen", email: "admin@university.edu.vn", avatar: null },
    action: "settings_change",
    target: "Cau hinh he thong",
    ip: "192.168.1.100",
    status: "success",
    details: "Thay doi nguong nhan dien: 85% -> 80%"
  },
  {
    id: "LOG008",
    timestamp: "2024-01-15 13:15:33",
    user: { name: "GV. Hoang Minh", email: "hoangminh@university.edu.vn", avatar: null },
    action: "report_export",
    target: "Bao cao chuyen can T1/2024",
    ip: "192.168.1.108",
    status: "success",
    details: "Xuat bao cao Excel"
  },
  {
    id: "LOG009",
    timestamp: "2024-01-15 12:50:20",
    user: { name: "Admin Tran", email: "admin2@university.edu.vn", avatar: null },
    action: "user_update",
    target: "Le Van Hung (SV2023067)",
    ip: "192.168.1.101",
    status: "success",
    details: "Cap nhat thong tin sinh vien"
  },
  {
    id: "LOG010",
    timestamp: "2024-01-15 12:30:15",
    user: { name: "System", email: "system@university.edu.vn", avatar: null },
    action: "backup_complete",
    target: "Database backup",
    ip: "10.0.0.1",
    status: "success",
    details: "Sao luu co so du lieu thanh cong"
  },
]

const actionTypes = [
  { value: "all", label: "Tat ca hanh dong" },
  { value: "user_create", label: "Tao nguoi dung" },
  { value: "user_update", label: "Cap nhat nguoi dung" },
  { value: "user_delete", label: "Xoa nguoi dung" },
  { value: "face_upload", label: "Tai len khuon mat" },
  { value: "face_delete", label: "Xoa khuon mat" },
  { value: "face_verify", label: "Xac minh khuon mat" },
  { value: "attendance_edit", label: "Sua diem danh" },
  { value: "session_start", label: "Bat dau phien" },
  { value: "session_end", label: "Ket thuc phien" },
  { value: "login_success", label: "Dang nhap" },
  { value: "login_failed", label: "Dang nhap that bai" },
  { value: "settings_change", label: "Thay doi cai dat" },
  { value: "report_export", label: "Xuat bao cao" },
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
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedAction, setSelectedAction] = useState("all")
  const [selectedStatus, setSelectedStatus] = useState("all")
  const [currentPage, setCurrentPage] = useState(1)

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = 
      log.user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.target.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.details.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesAction = selectedAction === "all" || log.action === selectedAction
    const matchesStatus = selectedStatus === "all" || log.status === selectedStatus
    return matchesSearch && matchesAction && matchesStatus
  })

  return (
    <AppShell role="admin">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Nhat ky hoat dong</h1>
            <p className="text-sm text-muted-foreground">
              Theo doi tat ca hoat dong trong he thong
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Lam moi
            </Button>
            <Button size="sm" className="bg-primary text-primary-foreground">
              <Download className="mr-2 h-4 w-4" />
              Xuat log
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-primary/10 p-2">
                  <History className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground">1,247</p>
                  <p className="text-sm text-muted-foreground">Tong hoat dong</p>
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
                  <p className="text-2xl font-bold text-success">1,189</p>
                  <p className="text-sm text-muted-foreground">Thanh cong</p>
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
                  <p className="text-2xl font-bold text-warning">45</p>
                  <p className="text-sm text-muted-foreground">Canh bao</p>
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
                  <p className="text-2xl font-bold text-destructive">13</p>
                  <p className="text-sm text-muted-foreground">Loi</p>
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
                  placeholder="Tim kiem theo nguoi dung, muc tieu, chi tiet..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Select value={selectedAction} onValueChange={setSelectedAction}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Loai hanh dong" />
                </SelectTrigger>
                <SelectContent>
                  {actionTypes.map(action => (
                    <SelectItem key={action.value} value={action.value}>
                      {action.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Trang thai" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tat ca</SelectItem>
                  <SelectItem value="success">Thanh cong</SelectItem>
                  <SelectItem value="warning">Canh bao</SelectItem>
                  <SelectItem value="error">Loi</SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="date"
                className="w-[150px]"
                defaultValue="2024-01-15"
              />
              <span className="text-muted-foreground">den</span>
              <Input
                type="date"
                className="w-[150px]"
                defaultValue="2024-01-15"
              />
            </div>
          </CardContent>
        </Card>

        {/* Audit Log Table */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Lich su hoat dong</CardTitle>
            <CardDescription>
              Hien thi {filteredLogs.length} ban ghi
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredLogs.map((log) => (
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
                      <StatusBadge
                        variant={
                          log.status === "success" ? "success" :
                          log.status === "warning" ? "warning" : "error"
                        }
                        size="sm"
                      >
                        {log.status === "success" ? "Thanh cong" :
                         log.status === "warning" ? "Canh bao" : "Loi"}
                      </StatusBadge>
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
                      {log.timestamp.split(" ")[1]}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {log.timestamp.split(" ")[0]}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Trang {currentPage} / 125
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Truoc
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => p + 1)}
                >
                  Sau
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
