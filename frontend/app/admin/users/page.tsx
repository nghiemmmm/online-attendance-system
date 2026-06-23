"use client"

import { useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RoleBadge } from "@/components/status-badge"
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { 
  Plus,
  Download,
  Search,
  Eye,
  Pencil,
  Lock,
  Unlock,
  Trash2,
  ChevronDown,
  ChevronUp
} from "lucide-react"

const mockUser = {
  name: "Admin System",
  email: "admin@university.edu.vn",
  avatar: ""
}

type UserRole = "student" | "lecturer" | "admin"
type UserStatus = "active" | "locked"

interface UserData {
  id: string
  name: string
  email: string
  role: UserRole
  status: UserStatus
  createdAt: string
  lastLogin: string
  studentId?: string
  faceDataStatus?: "approved" | "pending" | "none"
  classes?: string[]
}

const users: UserData[] = [
  { id: "1", name: "Nguyễn Văn A", email: "a.nguyen@student.edu.vn", role: "student", status: "active", createdAt: "01/09/2024", lastLogin: "26/05/2026", studentId: "SV001", faceDataStatus: "approved", classes: ["CS101", "CS201"] },
  { id: "2", name: "Trần Thị B", email: "b.tran@student.edu.vn", role: "student", status: "active", createdAt: "01/09/2024", lastLogin: "25/05/2026", studentId: "SV002", faceDataStatus: "pending", classes: ["CS101"] },
  { id: "3", name: "Lê Văn C", email: "c.le@student.edu.vn", role: "student", status: "locked", createdAt: "15/09/2024", lastLogin: "20/05/2026", studentId: "SV003", faceDataStatus: "approved", classes: ["CS201", "CS301"] },
  { id: "4", name: "Nguyễn Văn B", email: "b.nguyen@lecturer.edu.vn", role: "lecturer", status: "active", createdAt: "01/08/2024", lastLogin: "26/05/2026", classes: ["CS101", "CS201", "CS301"] },
  { id: "5", name: "Lê Thị M", email: "m.le@lecturer.edu.vn", role: "lecturer", status: "active", createdAt: "01/08/2024", lastLogin: "26/05/2026", classes: ["CS102", "CS202"] },
  { id: "6", name: "Admin System", email: "admin@university.edu.vn", role: "admin", status: "active", createdAt: "01/01/2024", lastLogin: "26/05/2026" },
]

export default function AdminUserManagement() {
  const [searchTerm, setSearchTerm] = useState("")
  const [roleFilter, setRoleFilter] = useState<string>("all")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [expandedUser, setExpandedUser] = useState<string | null>(null)
  const [createUserOpen, setCreateUserOpen] = useState(false)

  const filteredUsers = users.filter((user) => {
    if (roleFilter !== "all" && user.role !== roleFilter) return false
    if (statusFilter !== "all" && user.status !== statusFilter) return false
    if (searchTerm && !user.name.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !user.email.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !(user.studentId && user.studentId.toLowerCase().includes(searchTerm.toLowerCase()))) return false
    return true
  })

  return (
    <AppShell 
      role="admin" 
      user={mockUser} 
      breadcrumb="Quản lý người dùng"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Quản lý người dùng</h1>
            <span className="inline-flex items-center px-2.5 py-1 mt-2 rounded-full text-xs font-medium bg-[#DBEAFE] text-[#1E40AF]">
              {users.length} tài khoản
            </span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Import CSV
            </Button>
            <Button 
              onClick={() => setCreateUserOpen(true)}
              className="bg-[#0A2540] hover:bg-[#1A3A5C]"
            >
              <Plus className="w-4 h-4 mr-2" />
              Thêm người dùng
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-4">
              <div className="relative flex-1 min-w-[250px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
                <Input
                  placeholder="Tìm theo tên, email, mã số..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <div className="flex bg-[#F1F5F9] rounded-lg p-1">
                {[
                  { value: "all", label: "Tất cả" },
                  { value: "student", label: "Sinh viên" },
                  { value: "lecturer", label: "Giảng viên" },
                  { value: "admin", label: "Quản trị viên" },
                ].map((role) => (
                  <button
                    key={role.value}
                    onClick={() => setRoleFilter(role.value)}
                    className={cn(
                      "px-4 py-2 rounded-md text-sm font-medium transition-all",
                      roleFilter === role.value
                        ? "bg-white text-[#0A2540] shadow-sm"
                        : "text-[#64748B] hover:text-[#0F172A]"
                    )}
                  >
                    {role.label}
                  </button>
                ))}
              </div>

              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Trạng thái" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tất cả</SelectItem>
                  <SelectItem value="active">Kích hoạt</SelectItem>
                  <SelectItem value="locked">Bị khóa</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card className="border-[#E2E8F0] shadow-sm">
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]"></TableHead>
                  <TableHead>Người dùng</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Vai trò</TableHead>
                  <TableHead>Trạng thái</TableHead>
                  <TableHead>Ngày tạo</TableHead>
                  <TableHead>Hành động</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <>
                    <TableRow 
                      key={user.id}
                      className={cn(
                        "cursor-pointer hover:bg-[#F8FAFC]",
                        expandedUser === user.id && "bg-[#F8FAFC]"
                      )}
                      onClick={() => setExpandedUser(expandedUser === user.id ? null : user.id)}
                    >
                      <TableCell>
                        {expandedUser === user.id ? (
                          <ChevronUp className="w-4 h-4 text-[#64748B]" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-[#64748B]" />
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="w-9 h-9">
                            <AvatarFallback className="bg-[#0A2540] text-white text-sm">
                              {user.name.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <span className="font-medium">{user.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-[#64748B]">{user.email}</TableCell>
                      <TableCell>
                        <RoleBadge role={user.role} />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={cn(
                            "w-2 h-2 rounded-full",
                            user.status === "active" ? "bg-[#22C55E]" : "bg-[#EF4444]"
                          )} />
                          <span className={cn(
                            "text-sm",
                            user.status === "active" ? "text-[#22C55E]" : "text-[#EF4444]"
                          )}>
                            {user.status === "active" ? "Kích hoạt" : "Bị khóa"}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="text-[#64748B]">{user.createdAt}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="w-8 h-8">
                            <Eye className="w-4 h-4 text-[#64748B]" />
                          </Button>
                          <Button variant="ghost" size="icon" className="w-8 h-8">
                            <Pencil className="w-4 h-4 text-[#64748B]" />
                          </Button>
                          <Button variant="ghost" size="icon" className="w-8 h-8">
                            {user.status === "active" ? (
                              <Lock className="w-4 h-4 text-[#F59E0B]" />
                            ) : (
                              <Unlock className="w-4 h-4 text-[#22C55E]" />
                            )}
                          </Button>
                          <Button variant="ghost" size="icon" className="w-8 h-8">
                            <Trash2 className="w-4 h-4 text-[#EF4444]" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                    {expandedUser === user.id && (
                      <TableRow>
                        <TableCell colSpan={7} className="bg-[#F8FAFC]">
                          <div className="p-4 space-y-3">
                            <div className="grid grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-[#64748B]">Đăng nhập gần nhất:</span>
                                <p className="font-medium text-[#0F172A]">{user.lastLogin}</p>
                              </div>
                              {user.studentId && (
                                <div>
                                  <span className="text-[#64748B]">Mã sinh viên:</span>
                                  <p className="font-medium text-[#0F172A]">{user.studentId}</p>
                                </div>
                              )}
                              {user.faceDataStatus && (
                                <div>
                                  <span className="text-[#64748B]">Dữ liệu khuôn mặt:</span>
                                  <p className={cn(
                                    "font-medium",
                                    user.faceDataStatus === "approved" ? "text-[#22C55E]" :
                                    user.faceDataStatus === "pending" ? "text-[#F59E0B]" : "text-[#EF4444]"
                                  )}>
                                    {user.faceDataStatus === "approved" ? "Đã duyệt" :
                                     user.faceDataStatus === "pending" ? "Chờ duyệt" : "Chưa đăng ký"}
                                  </p>
                                </div>
                              )}
                              {user.classes && user.classes.length > 0 && (
                                <div>
                                  <span className="text-[#64748B]">Lớp học phần:</span>
                                  <p className="font-medium text-[#0F172A]">{user.classes.join(", ")}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                ))}
              </TableBody>
            </Table>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[#E2E8F0]">
              <p className="text-sm text-[#64748B]">
                Hiển thị {filteredUsers.length} / {users.length} người dùng
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled>Trước</Button>
                <Button variant="outline" size="sm" disabled>Sau</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Create User Modal */}
      <Dialog open={createUserOpen} onOpenChange={setCreateUserOpen}>
        <DialogContent className="max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Thêm người dùng mới</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Họ và tên <span className="text-red-500">*</span>
              </label>
              <Input placeholder="Nhập họ và tên" />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Email <span className="text-red-500">*</span>
              </label>
              <Input type="email" placeholder="Nhập email" />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Vai trò <span className="text-red-500">*</span>
              </label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn vai trò" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="student">Sinh viên</SelectItem>
                  <SelectItem value="lecturer">Giảng viên</SelectItem>
                  <SelectItem value="admin">Quản trị viên</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Mã sinh viên (nếu là sinh viên)
              </label>
              <Input placeholder="VD: SV001" />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Mật khẩu <span className="text-red-500">*</span>
              </label>
              <Input type="password" placeholder="Nhập mật khẩu" />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateUserOpen(false)}>
              Hủy
            </Button>
            <Button className="bg-[#0A2540] hover:bg-[#1A3A5C]">
              Tạo người dùng
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  )
}
