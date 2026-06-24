"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CourseClass } from "@/types/class"
import { ClassService } from "@/services/class.service"
import { LecturerService } from "@/services/lecturer.service"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import {
  AlertCircle,
  BookOpen,
  CalendarDays,
  Clock,
  Download,
  Loader2,
  Pencil,
  PlayCircle,
  Trash2,
  Users,
} from "lucide-react"


interface SessionForm {
  ngay_hoc: string
  gio_bat_dau: string
  gio_ket_thuc: string
  so_buoi: string
  so_phut_muon_toi_da: string
  nguong_nhan_dien: string
  ghi_chu: string
}

const emptySessionForm: SessionForm = {
  ngay_hoc: "",
  gio_bat_dau: "",
  gio_ket_thuc: "",
  so_buoi: "",
  so_phut_muon_toi_da: "15",
  nguong_nhan_dien: "0.6",
  ghi_chu: "",
}

export default function LecturerClassesPage() {
  const [profile, setProfile] = useState<{ name: string; email: string; maCanBo: number } | null>(null)
  const [classes, setClasses] = useState<CourseClass[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pendingClaimsCount, setPendingClaimsCount] = useState(0)
  const [selectedClass, setSelectedClass] = useState<CourseClass | null>(null)
  const [sessions, setSessions] = useState<any[]>([])
  const [warnings, setWarnings] = useState<any[]>([])
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [editingSessionId, setEditingSessionId] = useState<number | null>(null)
  const [sessionForm, setSessionForm] = useState<SessionForm>(emptySessionForm)
  const [students, setStudents] = useState<any[]>([])
  const [studentsLoading, setStudentsLoading] = useState(false)
  const [isStudentModalOpen, setIsStudentModalOpen] = useState(false)


  const fetchProfileAndClasses = async () => {
    setLoading(true)
    setError(null)
    try {
      const prof = await LecturerService.getProfile()
      setProfile(prof)
      const [classData, claimsCount] = await Promise.all([
        ClassService.getClasses(),
        prof.maCanBo ? LecturerService.getPendingClaimsCount(prof.maCanBo) : Promise.resolve(0),
      ])
      setClasses(classData)
      setPendingClaimsCount(claimsCount)
    } catch (err: any) {
      setError(err.message || "Da xay ra loi.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfileAndClasses()
  }, [])

  const resetSessionForm = () => {
    setEditingSessionId(null)
    setSessionForm(emptySessionForm)
  }

  const loadClassDetails = async (cls: CourseClass) => {
    setSelectedClass(cls)
    setSessionsLoading(true)
    resetSessionForm()
    try {
      const [sessionData, warningData] = await Promise.all([
        LecturerService.getClassSessions(cls.id),
        LecturerService.getClassWarnings(cls.id),
      ])
      setSessions(sessionData)
      setWarnings(warningData)
    } catch (err: any) {
      setError(err.message || "Khong the tai chi tiet lop hoc phan.")
    } finally {
      setSessionsLoading(false)
    }
  }

  const viewClassStudents = async (cls: CourseClass) => {
    setIsStudentModalOpen(true)
    setStudentsLoading(true)
    try {
      const studentData = await LecturerService.getClassStudents(cls.id)
      setStudents(studentData)
    } catch (err: any) {
      alert("Không thể tải danh sách sinh viên.")
    } finally {
      setStudentsLoading(false)
    }
  }


  const handleSessionSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!selectedClass) return

    const payload = {
      ma_lop_hoc_phan: selectedClass.id,
      ngay_hoc: sessionForm.ngay_hoc,
      gio_bat_dau: sessionForm.gio_bat_dau || null,
      gio_ket_thuc: sessionForm.gio_ket_thuc || null,
      so_buoi: sessionForm.so_buoi ? Number(sessionForm.so_buoi) : null,
      so_phut_muon_toi_da: Number(sessionForm.so_phut_muon_toi_da) || 15,
      nguong_nhan_dien: Number(sessionForm.nguong_nhan_dien) || 0.6,
      ghi_chu: sessionForm.ghi_chu || null,
      trang_thai: "CHUA_DIEM_DANH",
    }

    try {
      if (editingSessionId) {
        await LecturerService.updateSession(editingSessionId, payload)
      } else {
        await LecturerService.createSession(payload)
      }
      await loadClassDetails(selectedClass)
    } catch {
      alert("Khong the luu buoi hoc.")
    }
  }

  const handleEditSession = (session: any) => {
    setEditingSessionId(session.ma_buoi_hoc)
    setSessionForm({
      ngay_hoc: session.ngay_hoc || "",
      gio_bat_dau: session.gio_bat_dau || "",
      gio_ket_thuc: session.gio_ket_thuc || "",
      so_buoi: session.so_buoi?.toString() || "",
      so_phut_muon_toi_da: session.so_phut_muon_toi_da?.toString() || "15",
      nguong_nhan_dien: session.nguong_nhan_dien?.toString() || "0.6",
      ghi_chu: session.ghi_chu || "",
    })
  }

  const handleCancelSession = async (maBuoiHoc: number) => {
    if (!selectedClass) return
    if (!confirm("Ban co chac muon huy buoi hoc nay?")) return
    try {
      await LecturerService.cancelSession(maBuoiHoc)
      await loadClassDetails(selectedClass)
    } catch {
      alert("Khong the huy buoi hoc.")
    }
  }

  const handleStartSession = async (maBuoiHoc: number) => {
    try {
      await LecturerService.moDiemDanh(maBuoiHoc)
      window.location.href = `/lecturer/live/${maBuoiHoc}`
    } catch {
      alert("Khong the mo phien diem danh.")
    }
  }

  const userDisplayName = profile ? profile.name : "Giang vien"
  const userEmail = profile ? profile.email : "loading..."

  return (
    <AppShell
      role="lecturer"
      user={{ name: userDisplayName, email: userEmail, avatar: "" }}
      breadcrumb="Quan ly lop hoc phan"
      notificationCount={pendingClaimsCount}
    >
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Danh sach lop hoc phan</h1>
            <p className="text-[#64748B] mt-1">Quan ly lop, buoi hoc, diem danh va bao cao chuyen can.</p>
          </div>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0] shadow-sm">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Dang tai du lieu lop hoc phan...</p>
          </div>
        )}

        {!loading && error && (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <AlertCircle className="w-12 h-12 text-[#EF4444] mb-3" />
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Da xay ra loi</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchProfileAndClasses} variant="outline" className="border-[#EF4444] text-[#EF4444]">
                Thu lai
              </Button>
            </CardContent>
          </Card>
        )}

        {!loading && !error && classes.length === 0 && (
          <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
            <CardContent className="flex flex-col items-center justify-center py-20 text-center">
              <BookOpen className="w-12 h-12 text-[#64748B] mb-3" />
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Chua co lop hoc phan nao</h3>
              <p className="text-[#64748B] max-w-sm">Ban chua duoc phan cong lop hoc phan nao trong hoc ky nay.</p>
            </CardContent>
          </Card>
        )}

        {!loading && !error && classes.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {classes.map((cls) => (
              <Card key={cls.id} className="border-[#E2E8F0] shadow-sm hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg font-semibold text-[#0F172A] line-clamp-1" title={cls.tenHocPhan}>
                        {cls.tenHocPhan}
                      </CardTitle>
                      <p className="text-sm text-[#64748B] mt-1">Ma lop: {cls.maLop} - {cls.hocKy}</p>
                    </div>
                    <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-[#DCFCE7] text-[#166534]">
                      {cls.trangThai}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-5">
                    <div className="flex items-center gap-2 text-sm text-[#64748B] bg-[#F8FAFC] p-3 rounded-lg">
                      <Users className="w-5 h-5 text-[#0EA5E9]" />
                      <span className="font-medium">Si so:</span>
                      <span>{cls.siSoHienTai} / {cls.siSo} sinh vien</span>
                    </div>
                    <div className="flex items-center gap-3 pt-2">
                      <Button
                        className="flex-1 bg-[#0A2540] hover:bg-[#1A3A5C]"
                        onClick={() => loadClassDetails(cls)}
                      >
                        <PlayCircle className="w-4 h-4 mr-2" />
                        Quan ly buoi
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 text-[#0A2540] border-[#E2E8F0]"
                        onClick={() => loadClassDetails(cls)}
                      >
                        Xem chi tiet
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {selectedClass && (
          <div className="grid grid-cols-1 xl:grid-cols-[420px_1fr] gap-6">
            <Card className="border-[#E2E8F0] shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">{editingSessionId ? "Cap nhat buoi hoc" : "Tao buoi hoc"}</CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-4" onSubmit={handleSessionSubmit}>
                  <div className="grid grid-cols-2 gap-3">
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Ngay hoc
                      <input
                        type="date"
                        required
                        value={sessionForm.ngay_hoc}
                        onChange={(e) => setSessionForm({ ...sessionForm, ngay_hoc: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Buoi so
                      <input
                        type="number"
                        min="1"
                        value={sessionForm.so_buoi}
                        onChange={(e) => setSessionForm({ ...sessionForm, so_buoi: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Bat dau
                      <input
                        type="time"
                        value={sessionForm.gio_bat_dau}
                        onChange={(e) => setSessionForm({ ...sessionForm, gio_bat_dau: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Ket thuc
                      <input
                        type="time"
                        value={sessionForm.gio_ket_thuc}
                        onChange={(e) => setSessionForm({ ...sessionForm, gio_ket_thuc: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Phut muon toi da
                      <input
                        type="number"
                        min="0"
                        value={sessionForm.so_phut_muon_toi_da}
                        onChange={(e) => setSessionForm({ ...sessionForm, so_phut_muon_toi_da: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                    <label className="space-y-1 text-sm font-medium text-[#334155]">
                      Nguong nhan dien
                      <input
                        type="number"
                        step="0.05"
                        min="0"
                        max="1"
                        value={sessionForm.nguong_nhan_dien}
                        onChange={(e) => setSessionForm({ ...sessionForm, nguong_nhan_dien: e.target.value })}
                        className="w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                      />
                    </label>
                  </div>
                  <label className="space-y-1 text-sm font-medium text-[#334155] block">
                    Ghi chu
                    <textarea
                      value={sessionForm.ghi_chu}
                      onChange={(e) => setSessionForm({ ...sessionForm, ghi_chu: e.target.value })}
                      className="min-h-[72px] w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm"
                    />
                  </label>
                  <div className="flex gap-2">
                    <Button type="submit" className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                      {editingSessionId ? "Luu thay doi" : "Tao buoi hoc"}
                    </Button>
                    {editingSessionId && (
                      <Button type="button" variant="outline" onClick={resetSessionForm}>
                        Huy sua
                      </Button>
                    )}
                  </div>
                </form>
              </CardContent>
            </Card>

            <Card className="border-[#E2E8F0] shadow-sm">
              <CardHeader>
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <CardTitle className="text-lg">{selectedClass.tenHocPhan}</CardTitle>
                    <p className="text-sm text-[#64748B] mt-1">Danh sach buoi hoc va canh bao chuyen can</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      className="border-[#0EA5E9] text-[#0EA5E9] hover:bg-[#EAFAFF]"
                      onClick={() => viewClassStudents(selectedClass)}
                    >
                      <Users className="w-4 h-4 mr-1.5" />
                      Danh sách SV
                    </Button>
                    <Button variant="outline" onClick={() => LecturerService.downloadAttendanceReport(selectedClass.id, "excel")}>
                      <Download className="w-4 h-4 mr-2" />
                      Excel
                    </Button>
                    <Button variant="outline" onClick={() => LecturerService.downloadAttendanceReport(selectedClass.id, "csv")}>
                      <Download className="w-4 h-4 mr-2" />
                      CSV
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {sessionsLoading ? (
                  <div className="py-12 text-center text-[#64748B]">
                    <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-[#0EA5E9]" />
                    Dang tai buoi hoc...
                  </div>
                ) : sessions.length === 0 ? (
                  <div className="py-10 text-center text-[#64748B] border border-dashed border-[#CBD5E1] rounded-lg">
                    Chua co buoi hoc nao cho lop nay.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {sessions.map((session) => (
                      <div key={session.ma_buoi_hoc} className="flex flex-col gap-3 rounded-lg border border-[#E2E8F0] p-4 md:flex-row md:items-center md:justify-between">
                        <div>
                          <div className="flex items-center gap-2 font-semibold text-[#0F172A]">
                            <CalendarDays className="w-4 h-4 text-[#0EA5E9]" />
                            Buoi {session.so_buoi || "-"} - {session.ngay_hoc}
                          </div>
                          <div className="mt-1 flex flex-wrap gap-3 text-sm text-[#64748B]">
                            <span className="inline-flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              {session.gio_bat_dau || "--:--"} - {session.gio_ket_thuc || "--:--"}
                            </span>
                            <span>Muon toi da: {session.so_phut_muon_toi_da} phut</span>
                            <span>Nguong: {session.nguong_nhan_dien}</span>
                            <span className="font-medium text-[#0F172A]">{session.trang_thai || "CHUA_DIEM_DANH"}</span>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <Button size="sm" onClick={() => handleStartSession(session.ma_buoi_hoc)} className="bg-[#22C55E] hover:bg-[#16A34A]">
                            <PlayCircle className="w-4 h-4 mr-1" />
                            Mo phien
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => window.location.href = `/lecturer/live/${session.ma_buoi_hoc}`}>
                            Live
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleEditSession(session)}>
                            <Pencil className="w-4 h-4 mr-1" />
                            Sua
                          </Button>
                          <Button size="sm" variant="outline" className="text-[#EF4444]" onClick={() => handleCancelSession(session.ma_buoi_hoc)}>
                            <Trash2 className="w-4 h-4 mr-1" />
                            Huy
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-semibold text-[#0F172A] mb-3">Sinh vien nguy co cam thi</h3>
                  {warnings.length === 0 ? (
                    <p className="rounded-lg bg-[#F8FAFC] p-4 text-sm text-[#64748B]">
                      Chua co sinh vien vuot nguong canh bao vang.
                    </p>
                  ) : (
                    <div className="overflow-x-auto rounded-lg border border-[#E2E8F0]">
                      <table className="w-full text-sm">
                        <thead className="bg-[#F8FAFC] text-left text-[#475569]">
                          <tr>
                            <th className="px-4 py-3">Ma SV</th>
                            <th className="px-4 py-3">Ho ten</th>
                            <th className="px-4 py-3">Vang</th>
                            <th className="px-4 py-3">Ty le</th>
                            <th className="px-4 py-3">Trang thai</th>
                          </tr>
                        </thead>
                        <tbody>
                          {warnings.map((warning) => (
                            <tr key={warning.ma_sinh_vien} className="border-t border-[#E2E8F0]">
                              <td className="px-4 py-3">SV{String(warning.ma_sinh_vien).padStart(3, "0")}</td>
                              <td className="px-4 py-3">{warning.ho_ten}</td>
                              <td className="px-4 py-3">{warning.so_buoi_vang}/{warning.tong_so_buoi}</td>
                              <td className="px-4 py-3">{warning.ty_le_vang}%</td>
                              <td className="px-4 py-3 font-medium text-[#EF4444]">{warning.trang_thai_canh_bao}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      <Dialog open={isStudentModalOpen} onOpenChange={setIsStudentModalOpen}>
        <DialogContent className="max-w-2xl bg-white">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-[#0F172A]">
              Danh sách sinh viên lớp {selectedClass?.tenHocPhan}
            </DialogTitle>
            <DialogDescription className="text-sm text-[#64748B]">
              Mã lớp: {selectedClass?.id} | Sĩ số: {students.length} sinh viên
            </DialogDescription>
          </DialogHeader>

          <div className="mt-2">
            {studentsLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-[#0EA5E9] animate-spin mb-3" />
                <p className="text-sm text-[#64748B] font-medium">Đang tải danh sách sinh viên...</p>
              </div>
            ) : students.length === 0 ? (
              <div className="text-center py-12 text-[#64748B] border border-dashed border-[#CBD5E1] rounded-lg">
                Chưa có sinh viên nào đăng ký lớp học này.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-[#E2E8F0] max-h-[350px]">
                <table className="w-full text-sm">
                  <thead className="bg-[#F8FAFC] text-left text-[#475569] sticky top-0 border-b border-[#E2E8F0]">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Mã SV</th>
                      <th className="px-4 py-3 font-semibold">Họ và tên</th>
                      <th className="px-4 py-3 font-semibold">Email</th>
                      <th className="px-4 py-3 font-semibold">Số điện thoại</th>
                      <th className="px-4 py-3 font-semibold">Lớp khóa học</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E8F0]">
                    {students.map((student) => (
                      <tr key={student.ma_sinh_vien} className="hover:bg-[#F8FAFC] transition-colors">
                        <td className="px-4 py-3 font-medium text-[#0A2540]">
                          SV{String(student.ma_sinh_vien).padStart(3, "0")}
                        </td>
                        <td className="px-4 py-3 font-semibold text-[#0F172A]">
                          {`${student.ho || ""} ${student.ten || ""}`.trim()}
                        </td>
                        <td className="px-4 py-3 text-[#475569]">{student.google_email || "N/A"}</td>
                        <td className="px-4 py-3 text-[#475569]">{student.dien_thoai || "N/A"}</td>
                        <td className="px-4 py-3 text-[#475569]">{student.lop_khoa_hoc || "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </AppShell>
  )
}
