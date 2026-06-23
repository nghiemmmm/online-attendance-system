"use client"

import { useEffect, useState } from "react"
import { AppShell } from "@/components/app-shell"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { CourseClass } from "@/types/class"
import { AdminService } from "@/services/admin.service"
import { Loader2, AlertCircle, Plus, Search, Edit, Trash2, Users, BookOpen } from "lucide-react"

const mockUser = {
  name: "Quản Trị Viên",
  email: "admin@university.edu.vn",
  avatar: ""
}

export default function AdminClassesPage() {
  const [classes, setClasses] = useState<CourseClass[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Search
  const [searchQuery, setSearchQuery] = useState("")

  // Dialog State
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  
  // Form State
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    maLop: '',
    tenHocPhan: '',
    giangVien: '',
    hocKy: '',
    siSo: 50,
    trangThai: 'Đang học' as CourseClass['trangThai']
  })

  const fetchClasses = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await AdminService.getClasses()
      setClasses(data)
    } catch (err: any) {
      setError(err.message || "Đã xảy ra lỗi khi tải danh sách lớp học.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClasses()
  }, [])

  const openCreateDialog = () => {
    setEditingId(null)
    setFormData({
      maLop: '',
      tenHocPhan: '',
      giangVien: '',
      hocKy: 'HK1-2026',
      siSo: 50,
      trangThai: 'Sắp mở'
    })
    setIsDialogOpen(true)
  }

  const openEditDialog = (c: CourseClass) => {
    setEditingId(c.id)
    setFormData({
      maLop: c.maLop,
      tenHocPhan: c.tenHocPhan,
      giangVien: c.giangVien,
      hocKy: c.hocKy,
      siSo: c.siSo,
      trangThai: c.trangThai
    })
    setIsDialogOpen(true)
  }

  const openDeleteDialog = (id: number) => {
    setEditingId(id)
    setIsDeleteDialogOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      if (editingId) {
        const updated = await AdminService.updateClass(editingId, formData)
        setClasses(classes.map(c => c.id === editingId ? updated : c))
      } else {
        const created = await AdminService.createClass(formData)
        setClasses([created, ...classes])
      }
      setIsDialogOpen(false)
    } catch (err) {
      alert("Đã xảy ra lỗi khi lưu thông tin.")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!editingId) return
    setSubmitting(true)
    try {
      await AdminService.deleteClass(editingId)
      setClasses(classes.filter(c => c.id !== editingId))
      setIsDeleteDialogOpen(false)
    } catch (err) {
      alert("Đã xảy ra lỗi khi xóa lớp học.")
    } finally {
      setSubmitting(false)
    }
  }

  const filteredClasses = classes.filter(c => 
    c.maLop.toLowerCase().includes(searchQuery.toLowerCase()) || 
    c.tenHocPhan.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.giangVien.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <AppShell
      role="admin"
      user={mockUser}
      breadcrumb="Quản lý lớp học phần"
    >
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[#0F172A]">Danh sách lớp học phần</h1>
            <p className="text-[#64748B] mt-1">Thêm mới, cập nhật và quản lý toàn bộ các lớp đang hoạt động</p>
          </div>
          
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white shrink-0">
            <Plus className="w-4 h-4 mr-2" />
            Thêm lớp mới
          </Button>
        </div>

        {/* Data / Error Loading States */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-xl border border-[#E2E8F0]">
            <Loader2 className="w-10 h-10 text-[#0EA5E9] animate-spin mb-4" />
            <p className="text-[#64748B] font-medium">Đang đồng bộ dữ liệu lớp học...</p>
          </div>
        ) : error ? (
          <Card className="border-[#EF4444] bg-[#FEF2F2]">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 rounded-full bg-[#FEE2E2] flex items-center justify-center mb-4">
                <AlertCircle className="w-8 h-8 text-[#EF4444]" />
              </div>
              <h3 className="text-xl font-semibold text-[#991B1B] mb-2">Lỗi truy xuất hệ thống</h3>
              <p className="text-[#DC2626] mb-6 max-w-md">{error}</p>
              <Button onClick={fetchClasses} variant="outline" className="border-[#EF4444] text-[#EF4444] hover:bg-[#EF4444] hover:text-white">
                Thử lại ngay
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
              <Input 
                placeholder="Tìm kiếm theo mã lớp, tên môn học hoặc giảng viên..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="pl-9 border-[#E2E8F0] focus-visible:ring-[#0EA5E9]"
              />
            </div>

            {filteredClasses.length === 0 ? (
              <Card className="border-dashed border-2 border-[#E2E8F0] bg-[#F8FAFC]">
                <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                  <div className="w-16 h-16 rounded-full bg-[#E2E8F0] flex items-center justify-center mb-4">
                    <BookOpen className="w-8 h-8 text-[#64748B]" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Không tìm thấy lớp học</h3>
                  <p className="text-[#64748B] max-w-sm">
                    {searchQuery ? 'Không có dữ liệu phù hợp với từ khóa tìm kiếm.' : 'Hệ thống chưa có dữ liệu lớp học phần nào.'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="bg-white border border-[#E2E8F0] rounded-xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-[#F8FAFC] text-[#475569] font-medium border-b border-[#E2E8F0]">
                      <tr>
                        <th className="px-6 py-4 whitespace-nowrap">Mã Lớp</th>
                        <th className="px-6 py-4 whitespace-nowrap">Tên Học Phần</th>
                        <th className="px-6 py-4 whitespace-nowrap">Giảng Viên</th>
                        <th className="px-6 py-4 whitespace-nowrap">Học Kỳ</th>
                        <th className="px-6 py-4 whitespace-nowrap text-center">Sĩ số</th>
                        <th className="px-6 py-4 whitespace-nowrap">Trạng Thái</th>
                        <th className="px-6 py-4 whitespace-nowrap text-right">Thao Tác</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E2E8F0]">
                      {filteredClasses.map((c) => (
                        <tr key={c.id} className="hover:bg-[#F1F5F9] transition-colors">
                          <td className="px-6 py-4 font-semibold text-[#0F172A]">{c.maLop}</td>
                          <td className="px-6 py-4 text-[#334155]">{c.tenHocPhan}</td>
                          <td className="px-6 py-4 text-[#334155]">{c.giangVien}</td>
                          <td className="px-6 py-4 text-[#64748B]">{c.hocKy}</td>
                          <td className="px-6 py-4 text-center">
                            <div className="flex items-center justify-center text-[#334155]">
                              <Users className="w-3 h-3 mr-1 text-[#64748B]"/>
                              {c.siSoHienTai}/{c.siSo}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                              c.trangThai === 'Đang học' ? 'bg-[#DCFCE7] text-[#166534]' :
                              c.trangThai === 'Đã kết thúc' ? 'bg-[#F1F5F9] text-[#475569]' :
                              'bg-[#FEF9C3] text-[#92400E]'
                            }`}>
                              {c.trangThai}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex justify-end gap-2">
                              <Button size="icon" variant="ghost" onClick={() => openEditDialog(c)} className="h-8 w-8 text-[#0EA5E9] hover:text-[#0284C7] hover:bg-[#E0F2FE]">
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button size="icon" variant="ghost" onClick={() => openDeleteDialog(c.id)} className="h-8 w-8 text-[#EF4444] hover:text-[#DC2626] hover:bg-[#FEE2E2]">
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

        {/* Modal Thêm/Sửa */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>{editingId ? 'Cập nhật Lớp học' : 'Thêm Lớp học mới'}</DialogTitle>
              <DialogDescription>Điền thông tin chi tiết của lớp học phần vào biểu mẫu dưới đây.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maLop">Mã lớp</Label>
                  <Input id="maLop" value={formData.maLop} onChange={e => setFormData({...formData, maLop: e.target.value})} required placeholder="VD: CS101_HK1"/>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hocKy">Học kỳ</Label>
                  <Input id="hocKy" value={formData.hocKy} onChange={e => setFormData({...formData, hocKy: e.target.value})} required placeholder="VD: HK1-2026"/>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="tenHocPhan">Tên học phần</Label>
                <Input id="tenHocPhan" value={formData.tenHocPhan} onChange={e => setFormData({...formData, tenHocPhan: e.target.value})} required placeholder="VD: Lập trình Web"/>
              </div>
              <div className="space-y-2">
                <Label htmlFor="giangVien">Giảng viên phụ trách</Label>
                <Input id="giangVien" value={formData.giangVien} onChange={e => setFormData({...formData, giangVien: e.target.value})} required placeholder="VD: Nguyễn Văn B"/>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="siSo">Sĩ số tối đa</Label>
                  <Input id="siSo" type="number" min="1" max="200" value={formData.siSo} onChange={e => setFormData({...formData, siSo: parseInt(e.target.value) || 0})} required/>
                </div>
                <div className="space-y-2">
                  <Label>Trạng thái</Label>
                  <Select value={formData.trangThai} onValueChange={(v: any) => setFormData({...formData, trangThai: v})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Chọn trạng thái" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Sắp mở">Sắp mở</SelectItem>
                      <SelectItem value="Đang học">Đang học</SelectItem>
                      <SelectItem value="Đã kết thúc">Đã kết thúc</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter className="pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Hủy</Button>
                <Button type="submit" disabled={submitting} className="bg-[#0A2540] hover:bg-[#1A3A5C]">
                  {submitting && <Loader2 className="w-4 h-4 animate-spin mr-2"/>}
                  {editingId ? 'Lưu thay đổi' : 'Tạo lớp học'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Modal Xác nhận xóa */}
        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent className="sm:max-w-[400px]">
            <DialogHeader>
              <DialogTitle className="text-[#EF4444] flex items-center"><AlertCircle className="w-5 h-5 mr-2"/> Cảnh báo xóa lớp học</DialogTitle>
              <DialogDescription className="pt-2">
                Hành động này không thể hoàn tác. Mọi dữ liệu về điểm danh và sinh viên của lớp học này sẽ bị xóa vĩnh viễn khỏi hệ thống. Bạn có chắc chắn muốn tiếp tục?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-4">
              <Button type="button" variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>Hủy</Button>
              <Button onClick={handleDelete} disabled={submitting} className="bg-[#EF4444] hover:bg-[#DC2626] text-white">
                {submitting && <Loader2 className="w-4 h-4 animate-spin mr-2"/>}
                Xác nhận xóa
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

      </div>
    </AppShell>
  )
}
