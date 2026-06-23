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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { StatusBadge } from "@/components/status-badge"
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
  Mail
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

// Mock data for reports
const attendanceByDepartment = [
  { department: "CNTT", present: 892, absent: 108, late: 45, rate: 89.2 },
  { department: "QTKD", present: 756, absent: 144, late: 67, rate: 84.0 },
  { department: "KT", present: 634, absent: 66, late: 23, rate: 90.6 },
  { department: "NN", present: 445, absent: 55, late: 34, rate: 89.0 },
  { department: "Luat", present: 312, absent: 38, late: 18, rate: 89.1 },
]

const weeklyTrend = [
  { week: "T2", rate: 87.5, students: 2450 },
  { week: "T3", rate: 89.2, students: 2510 },
  { week: "T4", rate: 91.0, students: 2480 },
  { week: "T5", rate: 88.7, students: 2390 },
  { week: "T6", rate: 85.3, students: 2200 },
  { week: "T7", rate: 78.5, students: 1890 },
]

const monthlyComparison = [
  { month: "T1", thisYear: 88.5, lastYear: 85.2 },
  { month: "T2", thisYear: 89.2, lastYear: 86.1 },
  { month: "T3", thisYear: 90.1, lastYear: 87.3 },
  { month: "T4", thisYear: 87.8, lastYear: 84.9 },
  { month: "T5", thisYear: 91.2, lastYear: 88.0 },
]

const statusDistribution = [
  { name: "Co mat", value: 3039, color: "#22c55e" },
  { name: "Vang mat", value: 411, color: "#ef4444" },
  { name: "Di tre", value: 187, color: "#f59e0b" },
  { name: "Xin phep", value: 89, color: "#3b82f6" },
]

const topAbsentStudents = [
  { id: "SV001", name: "Nguyen Van A", department: "CNTT", absences: 12, rate: 60.0 },
  { id: "SV045", name: "Tran Thi B", department: "QTKD", absences: 10, rate: 66.7 },
  { id: "SV089", name: "Le Van C", department: "KT", absences: 9, rate: 70.0 },
  { id: "SV123", name: "Pham Thi D", department: "NN", absences: 8, rate: 73.3 },
  { id: "SV167", name: "Hoang Van E", department: "Luat", absences: 8, rate: 73.3 },
]

const classPerformance = [
  { class: "CNTT-K65A", students: 45, avgRate: 92.5, trend: "up" },
  { class: "QTKD-K65B", students: 42, avgRate: 88.2, trend: "down" },
  { class: "KT-K65A", students: 38, avgRate: 91.0, trend: "up" },
  { class: "NN-K65C", students: 35, avgRate: 85.5, trend: "down" },
  { class: "CNTT-K65B", students: 44, avgRate: 89.8, trend: "up" },
]

export default function AdminReportsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState("month")
  const [selectedDepartment, setSelectedDepartment] = useState("all")

  return (
    <AppShell role="admin">
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
            <Button variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Lam moi
            </Button>
            <Button variant="outline" size="sm">
              <Printer className="mr-2 h-4 w-4" />
              In bao cao
            </Button>
            <Button size="sm" className="bg-primary text-primary-foreground">
              <Download className="mr-2 h-4 w-4" />
              Xuat Excel
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Bo loc:</span>
              </div>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Thoi gian" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Tuan nay</SelectItem>
                  <SelectItem value="month">Thang nay</SelectItem>
                  <SelectItem value="semester">Hoc ky</SelectItem>
                  <SelectItem value="year">Nam hoc</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Khoa" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tat ca khoa</SelectItem>
                  <SelectItem value="cntt">Cong nghe thong tin</SelectItem>
                  <SelectItem value="qtkd">Quan tri kinh doanh</SelectItem>
                  <SelectItem value="kt">Ke toan</SelectItem>
                  <SelectItem value="nn">Ngoai ngu</SelectItem>
                  <SelectItem value="luat">Luat</SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="date"
                className="w-[150px]"
                defaultValue="2024-01-01"
              />
              <span className="text-muted-foreground">den</span>
              <Input
                type="date"
                className="w-[150px]"
                defaultValue="2024-01-31"
              />
            </div>
          </CardContent>
        </Card>

        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Tong sinh vien</p>
                  <p className="text-2xl font-bold text-foreground">3,726</p>
                  <p className="flex items-center gap-1 text-xs text-success">
                    <TrendingUp className="h-3 w-3" />
                    +2.5% so voi thang truoc
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
                  <p className="text-sm text-muted-foreground">Ti le chuyen can TB</p>
                  <p className="text-2xl font-bold text-foreground">88.7%</p>
                  <p className="flex items-center gap-1 text-xs text-success">
                    <TrendingUp className="h-3 w-3" />
                    +1.2% so voi thang truoc
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
                  <p className="text-sm text-muted-foreground">Tong buoi hoc</p>
                  <p className="text-2xl font-bold text-foreground">1,245</p>
                  <p className="text-xs text-muted-foreground">
                    Trong thang nay
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
                  <p className="text-sm text-muted-foreground">Canh bao chuyen can</p>
                  <p className="text-2xl font-bold text-destructive">47</p>
                  <p className="flex items-center gap-1 text-xs text-destructive">
                    <TrendingDown className="h-3 w-3" />
                    Duoi 70% chuyen can
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
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Tong quan</TabsTrigger>
            <TabsTrigger value="departments">Theo khoa</TabsTrigger>
            <TabsTrigger value="trends">Xu huong</TabsTrigger>
            <TabsTrigger value="alerts">Canh bao</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
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
                          formatter={(value: number) => [value.toLocaleString(), "Luot"]}
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
                          formatter={(value: number, name: string) => [
                            name === "rate" ? `${value}%` : value.toLocaleString(),
                            name === "rate" ? "Ti le" : "Sinh vien"
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
                      <Tooltip formatter={(value: number) => [`${value}%`, ""]} />
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
          </TabsContent>

          <TabsContent value="departments" className="space-y-4">
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
                            <StatusBadge 
                              variant={dept.rate >= 90 ? "success" : dept.rate >= 80 ? "warning" : "error"}
                            >
                              {dept.rate}%
                            </StatusBadge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
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
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
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
                            <StatusBadge variant={student.rate < 70 ? "error" : "warning"}>
                              {student.rate < 70 ? "Nguy co" : "Chu y"}
                            </StatusBadge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  )
}
