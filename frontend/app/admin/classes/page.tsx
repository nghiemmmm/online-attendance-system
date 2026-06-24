"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AdminClassPayload, AdminService, CanBoOption, HocPhanOption } from "@/services/admin.service"
import { AlertCircle, BookOpen, Edit, Loader2, Plus, Search, Trash2, Users } from "lucide-react"

type AdminClass = Awaited<ReturnType<typeof AdminService.getClasses>>[number]

const defaultForm = {
  ma_hoc_phan: "",
  ma_can_bo: "",
  hoc_ky: "1",
  nam_hoc: "2025-2026",
  ty_le_chuyen_can_toi_thieu: "0.8",
  trang_thai: "true",
}

export default function AdminClassesPage() {
  const [adminUser, setAdminUser] = useState({ name: "Admin", email: "admin@university.edu.vn", avatar: "" })
  const [classes, setClasses] = useState<AdminClass[]>([])
  const [subjects, setSubjects] = useState<HocPhanOption[]>([])
  const [lecturers, setLecturers] = useState<CanBoOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState(defaultForm)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [classData, subjectData, lecturerData] = await Promise.all([
        AdminService.getClasses(),
        AdminService.getSubjects(),
        AdminService.getLecturers(),
      ])
      setClasses(classData)
      setSubjects(subjectData)
      setLecturers(lecturerData)
    } catch (err: any) {
      setError(err.message || "Khong the tai du lieu lop hoc phan.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    AdminService.getProfile()
      .then((profile) => setAdminUser({ ...profile, avatar: "" }))
      .catch((err) => console.error("Loi tai profile admin:", err))
    fetchData()
  }, [])

  const openCreateDialog = () => {
    setEditingId(null)
    setFormData({
      ...defaultForm,
      ma_hoc_phan: subjects[0]?.ma_hoc_phan?.toString() || "",
      ma_can_bo: lecturers[0]?.ma_can_bo?.toString() || "",
    })
    setIsDialogOpen(true)
  }

  const openEditDialog = (item: AdminClass) => {
    setEditingId(item.id)
    setFormData({
      ma_hoc_phan: item.maHocPhan?.toString() || "",
      ma_can_bo: item.maCanBo?.toString() || "",
      hoc_ky: item.hocKyNumber?.toString() || "1",
      nam_hoc: item.namHoc || "2025-2026",
      ty_le_chuyen_can_toi_thieu: item.tyLeChuyenCanToiThieu?.toString() || "0.8",
      trang_thai: item.trangThai === "Đang học" ? "true" : "false",
    })
    setIsDialogOpen(true)
  }

  const buildPayload = (): AdminClassPayload => ({
    ma_hoc_phan: Number(formData.ma_hoc_phan),
    ma_can_bo: Number(formData.ma_can_bo),
    hoc_ky: Number(formData.hoc_ky),
    nam_hoc: formData.nam_hoc.trim(),
    ty_le_chuyen_can_toi_thieu: Number(formData.ty_le_chuyen_can_toi_thieu),
    trang_thai: formData.trang_thai === "true",
  })

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      const payload = buildPayload()
      if (editingId) {
        const updated = await AdminService.updateClass(editingId, payload)
        setClasses((prev) => prev.map((item) => (item.id === editingId ? updated : item)))
      } else {
        const created = await AdminService.createClass(payload)
        setClasses((prev) => [created, ...prev])
      }
      setIsDialogOpen(false)
    } catch (err: any) {
      alert(err.message || "Khong the luu lop hoc phan.")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!editingId) return
    setSubmitting(true)
    try {
      await AdminService.deleteClass(editingId)
      setClasses((prev) => prev.filter((item) => item.id !== editingId))
      setIsDeleteDialogOpen(false)
    } catch {
      alert("Khong the xoa lop hoc phan.")
    } finally {
      setSubmitting(false)
    }
  }

  const filteredClasses = classes.filter((item) => {
    const query = searchQuery.toLowerCase()
    return (
      item.maLop.toLowerCase().includes(query) ||
      item.tenHocPhan.toLowerCase().includes(query) ||
      item.giangVien.toLowerCase().includes(query) ||
      item.namHoc.toLowerCase().includes(query)
    )
  })

  return (
    <AppShell role="admin" user={adminUser} breadcrumb="Quan ly lop hoc phan">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Danh sach lop hoc phan</h1>
            <p className="text-[#64748B] mt-1">Tao lop theo hoc phan, phan cong giang vien va quan ly trang thai.</p>
          </div>
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white shrink-0">
            <Plus className="w-4 h-4 mr-2" />
            Them lop moi
          </Button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Dang dong bo du lieu lop hoc...</p>
          </div>
        ) : error ? (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <AlertCircle className="w-12 h-12 text-[#EF4444] mb-4" />
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Loi truy xuat he thong</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchData} variant="outline" className="border-[#EF4444] text-[#EF4444]">
                Thu lai
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
              <Input
                placeholder="Tim theo ma lop, hoc phan, giang vien, nam hoc..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-9 border-[#E2E8F0] focus-visible:ring-[#0EA5E9]"
              />
            </div>

            {filteredClasses.length === 0 ? (
              <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
                <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                  <BookOpen className="w-12 h-12 text-[#64748B] mb-3" />
                  <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Khong tim thay lop hoc</h3>
                  <p className="text-[#64748B] max-w-sm">Chua co du lieu phu hop voi bo loc hien tai.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="bg-white border border-[#E2E8F0] rounded-xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-[#F8FAFC] text-[#475569] font-medium border-b border-[#E2E8F0]">
                      <tr>
                        <th className="px-6 py-4 whitespace-nowrap">Ma lop</th>
                        <th className="px-6 py-4 whitespace-nowrap">Hoc phan</th>
                        <th className="px-6 py-4 whitespace-nowrap">Giang vien</th>
                        <th className="px-6 py-4 whitespace-nowrap">Hoc ky</th>
                        <th className="px-6 py-4 whitespace-nowrap text-center">Chuyen can toi thieu</th>
                        <th className="px-6 py-4 whitespace-nowrap">Trang thai</th>
                        <th className="px-6 py-4 whitespace-nowrap text-right">Thao tac</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E2E8F0]">
                      {filteredClasses.map((item) => (
                        <tr key={item.id} className="hover:bg-[#F1F5F9] transition-colors">
                          <td className="px-6 py-4 font-semibold text-[#0F172A]">LHP{item.id}</td>
                          <td className="px-6 py-4 text-[#334155]">{item.tenHocPhan}</td>
                          <td className="px-6 py-4 text-[#334155]">{item.giangVien}</td>
                          <td className="px-6 py-4 text-[#64748B]">{item.hocKy}</td>
                          <td className="px-6 py-4 text-center">
                            <span className="inline-flex items-center justify-center gap-1">
                              <Users className="w-3 h-3 text-[#64748B]" />
                              {Math.round(item.tyLeChuyenCanToiThieu * 100)}%
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                              item.trangThai === "Đang học"
                                ? "bg-[#DCFCE7] text-[#166534]"
                                : "bg-[#F1F5F9] text-[#475569]"
                            }`}>
                              {item.trangThai}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex justify-end gap-2">
                              <Button size="icon" variant="ghost" onClick={() => openEditDialog(item)} className="h-8 w-8 text-[#0EA5E9]">
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => {
                                  setEditingId(item.id)
                                  setIsDeleteDialogOpen(true)
                                }}
                                className="h-8 w-8 text-[#EF4444]"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-[560px]">
            <DialogHeader>
              <DialogTitle>{editingId ? "Cap nhat lop hoc phan" : "Them lop hoc phan moi"}</DialogTitle>
              <DialogDescription>Chon hoc phan, giang vien va thong tin hoc ky dung voi du lieu backend.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Hoc phan</Label>
                  <Select value={formData.ma_hoc_phan} onValueChange={(value) => setFormData({ ...formData, ma_hoc_phan: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Chon hoc phan" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects.map((subject) => (
                        <SelectItem key={subject.ma_hoc_phan} value={subject.ma_hoc_phan.toString()}>
                          {subject.ten_hoc_phan} ({subject.ma_hoc_phan})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Giang vien</Label>
                  <Select value={formData.ma_can_bo} onValueChange={(value) => setFormData({ ...formData, ma_can_bo: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Chon giang vien" />
                    </SelectTrigger>
                    <SelectContent>
                      {lecturers.map((lecturer) => (
                        <SelectItem key={lecturer.ma_can_bo} value={lecturer.ma_can_bo.toString()}>
                          {lecturer.ho} {lecturer.ten}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="hocKy">Hoc ky</Label>
                  <Input id="hocKy" type="number" min="1" max="3" value={formData.hoc_ky} onChange={(event) => setFormData({ ...formData, hoc_ky: event.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="namHoc">Nam hoc</Label>
                  <Input id="namHoc" value={formData.nam_hoc} onChange={(event) => setFormData({ ...formData, nam_hoc: event.target.value })} required placeholder="2025-2026" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tyLe">Ty le chuyen can toi thieu</Label>
                  <Input id="tyLe" type="number" min="0" max="1" step="0.05" value={formData.ty_le_chuyen_can_toi_thieu} onChange={(event) => setFormData({ ...formData, ty_le_chuyen_can_toi_thieu: event.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label>Trang thai</Label>
                  <Select value={formData.trang_thai} onValueChange={(value) => setFormData({ ...formData, trang_thai: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Chon trang thai" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">Dang hoc</SelectItem>
                      <SelectItem value="false">Da ket thuc</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <DialogFooter className="pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Huy</Button>
                <Button type="submit" disabled={submitting} className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                  {submitting && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  {editingId ? "Luu thay doi" : "Tao lop hoc"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent className="sm:max-w-[400px]">
            <DialogHeader>
              <DialogTitle className="text-[#EF4444] flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Xoa lop hoc phan
              </DialogTitle>
              <DialogDescription className="pt-2">Hanh dong nay co the bi chan neu lop da co du lieu lien quan.</DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-4">
              <Button type="button" variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>Huy</Button>
              <Button onClick={handleDelete} disabled={submitting} className="bg-[#EF4444] hover:bg-[#DC2626] text-white">
                {submitting && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                Xac nhan xoa
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppShell>
  )
}
