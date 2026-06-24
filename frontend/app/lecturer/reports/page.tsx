"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AttendanceReport } from "@/types/lecturer"
import { LecturerService } from "@/services/lecturer.service"
import { Loader2, AlertCircle, BarChart3, Download, Users, CheckCircle } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function LecturerReportsPage() {
  const [lecturerUser, setLecturerUser] = useState({
    name: "Giảng viên",
    email: "gv@university.edu.vn",
    avatar: ""
  })
  const [reports, setReports] = useState<AttendanceReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null)

  const fetchReports = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await LecturerService.getReports()
      setReports(data)
      if (data.length > 0) {
        setSelectedReportId(data[0].id)
      }
    } catch (err: any) {
      setError(err.message || "Đã xảy ra lỗi khi tải báo cáo.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    LecturerService.getProfile()
      .then(profile => {
        setLecturerUser({
          name: profile.name,
          email: profile.email,
          avatar: ""
        })
      })
      .catch(err => console.error("Lỗi tải thông tin giảng viên:", err))
    fetchReports()
  }, [])

  const selectedReport = reports.find(r => r.id === selectedReportId)

  return (
    <AppShell
      role="lecturer"
      user={lecturerUser}
      breadcrumb="Thống kê & Báo cáo"
    >
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Báo cáo chuyên cần</h1>
            <p className="text-[#64748B] mt-1">Theo dõi và phân tích tình hình học tập của sinh viên</p>
          </div>
          <Button disabled={!selectedReport || loading} className="bg-[#0A2540] hover:bg-[#1A3A5C] shrink-0">
            <Download className="w-4 h-4 mr-2" />
            Xuất Excel
          </Button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang phân tích dữ liệu...</p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[#FEE2E2] flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-[#EF4444]" />
              </div>
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Lỗi truy xuất báo cáo</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchReports} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại ngay
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Empty */}
        {!loading && !error && reports.length === 0 && (
          <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
            <CardContent className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-full bg-[#E2E8F0] flex items-center justify-center mb-4">
                <BarChart3 className="w-8 h-8 text-[#64748B]" />
              </div>
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Chưa có dữ liệu thống kê</h3>
              <p className="text-[#64748B] max-w-sm">
                Bạn chưa mở phiên điểm danh nào trong học kỳ này nên chưa có báo cáo.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Success */}
        {!loading && !error && selectedReport && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Lớp học list */}
            <div className="lg:col-span-1 space-y-3">
              <h3 className="font-semibold text-[#0F172A] px-1">Lớp học phần</h3>
              {reports.map(report => (
                <div 
                  key={report.id}
                  onClick={() => setSelectedReportId(report.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    selectedReportId === report.id 
                      ? 'bg-[#0A2540] text-white border-[#0A2540] shadow-md' 
                      : 'bg-white border-[#E2E8F0] hover:border-[#0EA5E9] text-[#0F172A]'
                  }`}
                >
                  <p className="font-semibold line-clamp-1">{report.subjectName}</p>
                  <p className={`text-xs mt-1 ${selectedReportId === report.id ? 'text-white/80' : 'text-[#64748B]'}`}>
                    {report.subjectCode} • {report.totalStudents} SV
                  </p>
                </div>
              ))}
            </div>

            {/* Dashboard chi tiết */}
            <div className="lg:col-span-3 space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <Card className="shadow-sm border-[#E2E8F0]">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-[#64748B]">Sĩ số</p>
                        <p className="text-2xl font-bold text-[#0F172A] mt-1">{selectedReport.totalStudents}</p>
                      </div>
                      <div className="p-2 bg-[#F1F5F9] rounded-lg"><Users className="w-4 h-4 text-[#475569]" /></div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border-[#E2E8F0]">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-[#64748B]">Đã học</p>
                        <p className="text-2xl font-bold text-[#0F172A] mt-1">{selectedReport.completedSessions}/{selectedReport.totalSessions}</p>
                      </div>
                      <div className="p-2 bg-[#EFF6FF] rounded-lg"><CheckCircle className="w-4 h-4 text-[#3B82F6]" /></div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border-[#E2E8F0]">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-[#64748B]">Chuyên cần</p>
                        <p className="text-2xl font-bold text-[#22C55E] mt-1">{selectedReport.averageAttendanceRate}%</p>
                      </div>
                      <div className="p-2 bg-[#DCFCE7] rounded-lg"><BarChart3 className="w-4 h-4 text-[#22C55E]" /></div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border-[#E2E8F0]">
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-[#64748B]">Cảnh báo</p>
                        <p className="text-2xl font-bold text-[#EF4444] mt-1">2</p>
                      </div>
                      <div className="p-2 bg-[#FEE2E2] rounded-lg"><AlertCircle className="w-4 h-4 text-[#EF4444]" /></div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="shadow-sm border-[#E2E8F0]">
                <CardHeader>
                  <CardTitle>Biểu đồ chuyên cần theo buổi</CardTitle>
                  <CardDescription>Số liệu sinh viên Có mặt, Đi muộn, và Vắng mặt qua các buổi học đã diễn ra</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={selectedReport.dataPoints} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis dataKey="date" tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                        <YAxis tick={{fontSize: 12}} tickLine={false} axisLine={false} />
                        <Tooltip cursor={{fill: '#F8FAFC'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                        <Legend wrapperStyle={{fontSize: '12px', paddingTop: '10px'}} />
                        <Bar name="Có mặt" dataKey="present" stackId="a" fill="#22C55E" radius={[0, 0, 4, 4]} />
                        <Bar name="Đi muộn" dataKey="late" stackId="a" fill="#F59E0B" />
                        <Bar name="Vắng mặt" dataKey="absent" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
