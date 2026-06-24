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
import {
  BarChart3,
  Download,
  FileSpreadsheet,
  TrendingUp,
  TrendingDown,
  Users,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Filter,
  RefreshCw,
  Printer,
  Mail,
  Loader2
} from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from "recharts"
import { AdminService } from "@/services/admin.service"

export default function AdminReportsPage() {
  const [adminUser, setAdminUser] = useState({
    name: "Admin",
    email: "admin@university.edu.vn",
    avatar: ""
  })
  const [summary, setSummary] = useState({
    total_students: 0,
    avg_attendance_rate: 0,
    total_sessions: 0,
    attendance_warnings: 0
  })
  const [attendanceByDepartment, setAttendanceByDepartment] = useState<any[]>([])
  const [weeklyTrend, setWeeklyTrend] = useState<any[]>([])
  const [monthlyComparison, setMonthlyComparison] = useState<any[]>([])
  const [statusDistribution, setStatusDistribution] = useState<any[]>([])
  const [topAbsentStudents, setTopAbsentStudents] = useState<any[]>([])
  const [classPerformance, setClassPerformance] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedPeriod, setSelectedPeriod] = useState("month")
  const [selectedDepartment, setSelectedDepartment] = useState("all")
  const [activeTab, setActiveTab] = useState("overview")

  const fetchReportStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await AdminService.getReportStats()
      if (data) {
        setSummary(data.summary || {
          total_students: 0,
          avg_attendance_rate: 0,
          total_sessions: 0,
          attendance_warnings: 0
        })
        setAttendanceByDepartment(data.attendanceByDepartment || [])
        setWeeklyTrend(data.weeklyTrend || [])
        setMonthlyComparison(data.monthlyComparison || [])
        setStatusDistribution(data.statusDistribution || [])
        setTopAbsentStudents(data.topAbsentStudents || [])
        setClassPerformance(data.classPerformance || [])
      }
    } catch (err: any) {
      console.error(err)
      setError("Không thể tải thông tin báo cáo thống kê từ máy chủ.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    AdminService.getProfile()
      .then(p => setAdminUser({ ...p, avatar: "" }))
      .catch(err => console.error("Lỗi tải profile admin:", err))
    fetchReportStats()
  }, [])

  return (
    <AppShell role="admin" user={adminUser} breadcrumb="Báo cáo & Thống kê">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Bao cao & Thong ke</h1>
            <p className="text-sm text-muted-foreground">
              Phan tich du lieu diem danh toan truong
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={fetchReportStats} disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Làm mới
            </Button>
            <Button variant="outline" size="sm">
              <Printer className="mr-2 h-4 w-4" />
              In báo cáo
            </Button>
            <Button size="sm" className="bg-primary text-primary-foreground">
              <Download className="mr-2 h-4 w-4" />
              Xuất Excel
            </Button>
          </div>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0] shadow-sm">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải báo cáo thống kê...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle className="w-12 h-12 text-[#EF4444] mb-3" />
              <h3 className="text-lg font-semibold text-[#991B1B] mb-1">Đã xảy ra lỗi</h3>
              <p className="text-[#DC2626] mb-4 max-w-md text-sm">{error}</p>
              <Button onClick={fetchReportStats} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && (
          <>
            {/* Filters */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Bộ lọc:</span>
                  </div>
                  <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Thời gian" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="week">Tuần này</SelectItem>
                      <SelectItem value="month">Tháng này</SelectItem>
                      <SelectItem value="semester">Học kỳ</SelectItem>
                      <SelectItem value="year">Năm học</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Khoa" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Tất cả khoa</SelectItem>
                      <SelectItem value="cntt">Công nghệ thông tin</SelectItem>
                      <SelectItem value="qtkd">Quản trị kinh doanh</SelectItem>
                      <SelectItem value="kt">Kế toán</SelectItem>
                      <SelectItem value="nn">Ngoại ngữ</SelectItem>
                      <SelectItem value="luat">Luật</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Summary Stats */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Tổng sinh viên</p>
                      <p className="text-2xl font-bold text-foreground">{summary.total_students.toLocaleString()}</p>
                      <p className="flex items-center gap-1 text-xs text-success">
                        <TrendingUp className="h-3 w-3" />
                        +2.5% so với tháng trước
                      </p>
                    </div>
                    <div className="rounded-full bg-primary/10 p-3">
                      <Users className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Tỉ lệ chuyên cần TB</p>
                      <p className="text-2xl font-bold text-foreground">{summary.avg_attendance_rate}%</p>
                      <p className="flex items-center gap-1 text-xs text-success">
                        <TrendingUp className="h-3 w-3" />
                        +1.2% so với tháng trước
                      </p>
                    </div>
                    <div className="rounded-full bg-success/10 p-3">
                      <CheckCircle2 className="h-6 w-6 text-success" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Tổng buổi học</p>
                      <p className="text-2xl font-bold text-foreground">{summary.total_sessions.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">
                        Đã kết thúc
                      </p>
                    </div>
                    <div className="rounded-full bg-accent/10 p-3">
                      <Calendar className="h-6 w-6 text-accent" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Cảnh báo chuyên cần</p>
                      <p className="text-2xl font-bold text-destructive">{summary.attendance_warnings}</p>
                      <p className="flex items-center gap-1 text-xs text-destructive">
                        <TrendingDown className="h-3 w-3" />
                        Vắng từ 3 buổi trở lên
                      </p>
                    </div>
                    <div className="rounded-full bg-destructive/10 p-3">
                      <AlertTriangle className="h-6 w-6 text-destructive" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

        {/* Charts */}
        <div className="flex border-b border-border space-x-6 mb-4">
          <button 
            className={cn("pb-2 px-1 text-sm font-medium border-b-2 transition-colors", activeTab === "overview" ? "border-primary border-b-2 text-primary" : "border-transparent text-muted-foreground hover:text-foreground")}
            onClick={() => setActiveTab("overview")}
          >
            Tổng quan
          </button>
          <button 
            className={cn("pb-2 px-1 text-sm font-medium border-b-2 transition-colors", activeTab === "departments" ? "border-primary border-b-2 text-primary" : "border-transparent text-muted-foreground hover:text-foreground")}
            onClick={() => setActiveTab("departments")}
          >
            Theo khoa
          </button>
          <button 
            className={cn("pb-2 px-1 text-sm font-medium border-b-2 transition-colors", activeTab === "trends" ? "border-primary border-b-2 text-primary" : "border-transparent text-muted-foreground hover:text-foreground")}
            onClick={() => setActiveTab("trends")}
          >
            Hiệu suất & Xu hướng
          </button>
          <button 
            className={cn("pb-2 px-1 text-sm font-medium border-b-2 transition-colors", activeTab === "alerts" ? "border-primary border-b-2 text-primary" : "border-transparent text-muted-foreground hover:text-foreground")}
            onClick={() => setActiveTab("alerts")}
          >
            Cảnh báo
          </button>
        </div>

        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              {/* Attendance Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Phan bo trang thai diem danh</CardTitle>
                  <CardDescription>Thang 01/2024</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={statusDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {statusDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                         <Tooltip 
                           formatter={(value: any) => [value?.toLocaleString() || "0", "Lượt"]}
                         />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Weekly Trend */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Ti le chuyen can theo ngay</CardTitle>
                  <CardDescription>Tuan hien tai</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={weeklyTrend}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis dataKey="week" className="text-xs" />
                        <YAxis domain={[70, 100]} className="text-xs" />
                         <Tooltip 
                           formatter={(value: any, name: any) => [
                             name === "rate" ? `${value}%` : value?.toLocaleString() || "0",
                             name === "rate" ? "Tỉ lệ" : "Sinh viên"
                           ]}
                         />
                        <Area
                          type="monotone"
                          dataKey="rate"
                          stroke="hsl(var(--primary))"
                          fill="hsl(var(--primary))"
                          fillOpacity={0.2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Monthly Comparison */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">So sanh chuyen can theo thang</CardTitle>
                <CardDescription>Nam 2024 vs 2023</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={monthlyComparison}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis dataKey="month" className="text-xs" />
                      <YAxis domain={[80, 95]} className="text-xs" />
                       <Tooltip formatter={(value: any) => [`${value}%`, ""]} />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="thisYear"
                        name="2024"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        dot={{ fill: "hsl(var(--primary))" }}
                      />
                      <Line
                        type="monotone"
                        dataKey="lastYear"
                        name="2023"
                        stroke="hsl(var(--muted-foreground))"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ fill: "hsl(var(--muted-foreground))" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "departments" && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Chuyen can theo khoa</CardTitle>
                <CardDescription>Thong ke chi tiet theo tung khoa</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={attendanceByDepartment} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis type="number" className="text-xs" />
                      <YAxis dataKey="department" type="category" className="text-xs" width={60} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="present" name="Co mat" fill="#22c55e" stackId="a" />
                      <Bar dataKey="late" name="Di tre" fill="#f59e0b" stackId="a" />
                      <Bar dataKey="absent" name="Vang mat" fill="#ef4444" stackId="a" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Department Table */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Chi tiet theo khoa</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="px-4 py-3 text-left font-medium text-muted-foreground">Khoa</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">Co mat</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">Di tre</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">Vang mat</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">Ti le</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendanceByDepartment.map((dept) => (
                        <tr key={dept.department} className="border-b border-border">
                          <td className="px-4 py-3 font-medium text-foreground">{dept.department}</td>
                          <td className="px-4 py-3 text-right text-success">{dept.present}</td>
                          <td className="px-4 py-3 text-right text-warning">{dept.late}</td>
                          <td className="px-4 py-3 text-right text-destructive">{dept.absent}</td>
                          <td className="px-4 py-3 text-right">
                             <span className={cn(
                               "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                               dept.rate >= 90 ? "bg-emerald-500/10 text-emerald-400" :
                               dept.rate >= 80 ? "bg-amber-500/10 text-amber-400" :
                               "bg-rose-500/10 text-rose-400"
                             )}>
                               {dept.rate}%
                             </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "trends" && (
          <div className="space-y-4">
            {/* Class Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Hieu suat lop hoc</CardTitle>
                <CardDescription>Xep hang theo ti le chuyen can</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {classPerformance.map((cls, index) => (
                    <div key={cls.class} className="flex items-center gap-4">
                      <span className="w-6 text-center font-bold text-muted-foreground">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{cls.class}</span>
                          <div className="flex items-center gap-2">
                            {cls.trend === "up" ? (
                              <TrendingUp className="h-4 w-4 text-success" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-destructive" />
                            )}
                            <span className="font-semibold text-foreground">{cls.avgRate}%</span>
                          </div>
                        </div>
                        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
                          <div
                            className={`h-full rounded-full ${
                              cls.avgRate >= 90 ? "bg-success" : cls.avgRate >= 80 ? "bg-warning" : "bg-destructive"
                            }`}
                            style={{ width: `${cls.avgRate}%` }}
                          />
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {cls.students} sinh vien
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "alerts" && (
          <div className="space-y-4">
            {/* Alert Summary */}
            <div className="grid gap-4 md:grid-cols-3">
              <Card className="border-destructive/50 bg-destructive/5">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <XCircle className="h-8 w-8 text-destructive" />
                    <div>
                      <p className="text-2xl font-bold text-destructive">12</p>
                      <p className="text-sm text-muted-foreground">Nguy co bi cam thi</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-warning/50 bg-warning/5">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-8 w-8 text-warning" />
                    <div>
                      <p className="text-2xl font-bold text-warning">35</p>
                      <p className="text-sm text-muted-foreground">Can theo doi</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-primary/50 bg-primary/5">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <Mail className="h-8 w-8 text-primary" />
                    <div>
                      <p className="text-2xl font-bold text-primary">47</p>
                      <p className="text-sm text-muted-foreground">Email canh bao da gui</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Top Absent Students */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base">Sinh vien vang nhieu nhat</CardTitle>
                    <CardDescription>Top 5 sinh vien can chu y</CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <Mail className="mr-2 h-4 w-4" />
                    Gui canh bao
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="px-4 py-3 text-left font-medium text-muted-foreground">MSSV</th>
                        <th className="px-4 py-3 text-left font-medium text-muted-foreground">Ho ten</th>
                        <th className="px-4 py-3 text-left font-medium text-muted-foreground">Khoa</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">So buoi vang</th>
                        <th className="px-4 py-3 text-right font-medium text-muted-foreground">Ti le</th>
                        <th className="px-4 py-3 text-center font-medium text-muted-foreground">Trang thai</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topAbsentStudents.map((student) => (
                        <tr key={student.id} className="border-b border-border">
                          <td className="px-4 py-3 font-mono text-sm text-foreground">{student.id}</td>
                          <td className="px-4 py-3 font-medium text-foreground">{student.name}</td>
                          <td className="px-4 py-3 text-muted-foreground">{student.department}</td>
                          <td className="px-4 py-3 text-right font-semibold text-destructive">
                            {student.absences}
                          </td>
                          <td className="px-4 py-3 text-right text-foreground">{student.rate}%</td>
                          <td className="px-4 py-3 text-center">
                             <span className={cn(
                               "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium",
                               student.rate < 70 ? "bg-rose-500/10 text-rose-400" : "bg-amber-500/10 text-amber-400"
                             )}>
                               {student.rate < 70 ? "Nguy cơ" : "Chú ý"}
                             </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
          </>
        )}
      </div>
    </AppShell>
  )
}
