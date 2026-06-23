"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { StudentClaim } from "@/types/student"
import { StudentService } from "@/services/student.service"
import { Loader2, AlertCircle, MessageSquareWarning, Plus, Clock, CheckCircle, XCircle } from "lucide-react"

const mockUser = {
  name: "Nguyễn Tuấn A",
  email: "tuan.a@student.edu.vn",
  avatar: ""
}

export default function StudentClaimsPage() {
  const [claims, setClaims] = useState<StudentClaim[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Form state
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    subjectCode: '',
    sessionNumber: '',
    reason: ''
  })

  const fetchClaims = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await StudentService.getClaims()
      setClaims(data)
    } catch (err: any) {
      setError(err.message || "Đã xảy ra lỗi khi tải dữ liệu.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClaims()
  }, [])

  const handleSubmitClaim = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.subjectCode || !formData.reason) return
    
    setSubmitting(true)
    try {
      const newClaim = await StudentService.submitClaim({
        subjectCode: formData.subjectCode,
        sessionNumber: parseInt(formData.sessionNumber) || 1,
        reason: formData.reason
      })
      setClaims([newClaim, ...claims])
      setIsDialogOpen(false)
      setFormData({ subjectCode: '', sessionNumber: '', reason: '' })
    } catch (err) {
      alert("Đã xảy ra lỗi khi gửi khiếu nại.")
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-5 h-5 text-[#22C55E]" />
      case 'rejected': return <XCircle className="w-5 h-5 text-[#EF4444]" />
      default: return <Clock className="w-5 h-5 text-[#F59E0B]" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return <span className="text-[#166534] bg-[#DCFCE7] px-2 py-1 rounded-full text-xs font-medium">Được chấp thuận</span>
      case 'rejected': return <span className="text-[#991B1B] bg-[#FEE2E2] px-2 py-1 rounded-full text-xs font-medium">Bị từ chối</span>
      default: return <span className="text-[#92400E] bg-[#FEF9C3] px-2 py-1 rounded-full text-xs font-medium">Đang chờ duyệt</span>
    }
  }

  return (
    <AppShell
      role="student"
      user={mockUser}
      breadcrumb="Khiếu nại điểm danh"
    >
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Lịch sử khiếu nại</h1>
            <p className="text-[#64748B] mt-1">Gửi và theo dõi kết quả xử lý khiếu nại điểm danh của bạn</p>
          </div>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white shrink-0">
                <Plus className="w-4 h-4 mr-2" />
                Gửi khiếu nại mới
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Tạo khiếu nại mới</DialogTitle>
                <DialogDescription>
                  Gửi yêu cầu xem xét lại kết quả điểm danh cho giảng viên.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmitClaim} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="subject">Mã môn học</Label>
                  <Input 
                    id="subject" 
                    placeholder="VD: CS101" 
                    value={formData.subjectCode}
                    onChange={(e) => setFormData({...formData, subjectCode: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="session">Buổi học số</Label>
                  <Input 
                    id="session" 
                    type="number" 
                    placeholder="VD: 5" 
                    value={formData.sessionNumber}
                    onChange={(e) => setFormData({...formData, sessionNumber: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reason">Lý do khiếu nại</Label>
                  <textarea 
                    id="reason" 
                    className="w-full min-h-[100px] flex rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Trình bày rõ lý do hệ thống điểm danh sai sót..."
                    value={formData.reason}
                    onChange={(e) => setFormData({...formData, reason: e.target.value})}
                    required
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Hủy</Button>
                  <Button type="submit" disabled={submitting} className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                    {submitting && <Loader2 className="w-4 h-4 animate-spin mr-2"/>}
                    Gửi yêu cầu
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang tải lịch sử khiếu nại...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[#FEE2E2] flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-[#EF4444]" />
              </div>
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Lỗi kết nối</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchClaims} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại ngay
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && claims.length === 0 && (
          <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
            <CardContent className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-full bg-[#E2E8F0] flex items-center justify-center mb-4">
                <MessageSquareWarning className="w-8 h-8 text-[#64748B]" />
              </div>
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Chưa có khiếu nại nào</h3>
              <p className="text-[#64748B] max-w-sm">
                Bạn chưa gửi yêu cầu khiếu nại điểm danh nào cho giảng viên.
              </p>
            </CardContent>
          </Card>
        )}

        {!loading && !error && claims.length > 0 && (
          <div className="space-y-4">
            {claims.map((claim) => (
              <Card key={claim.id} className="border-[#E2E8F0] hover:border-[#0EA5E9] transition-colors">
                <CardContent className="p-5">
                  <div className="flex flex-col md:flex-row md:items-start gap-4">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="mt-1">
                        {getStatusIcon(claim.status)}
                      </div>
                      <div className="space-y-2 flex-1">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <h3 className="font-semibold text-[#0F172A] text-lg">
                            {claim.subjectCode} - {claim.subjectName}
                          </h3>
                          <div>{getStatusText(claim.status)}</div>
                        </div>
                        <p className="text-sm text-[#64748B]">Buổi {claim.sessionNumber} • Lịch học: {claim.date} • Đã gửi: {claim.submittedAt}</p>
                        <div className="bg-[#F8FAFC] p-3 rounded-md mt-2 border border-[#E2E8F0]">
                          <p className="text-sm text-[#334155]">
                            <span className="font-medium text-[#0F172A]">Lý do gửi:</span> {claim.reason}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
