"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AdminService, HocPhanOption } from "@/services/admin.service";
import { BookOpen, Pencil, Plus, Search, Trash2 } from "lucide-react";

type SubjectForm = {
  course_id: string;
  course_name: string;
  credit_count: string;
  description: string;
  status: string;
};

const emptyForm: SubjectForm = {
  course_id: "",
  course_name: "",
  credit_count: "3",
  description: "",
  status: "true",
};

export default function AdminSubjectsPage() {
  const [user, setUser] = useState({ name: "Admin", email: "admin@university.edu.vn" });
  const [subjects, setSubjects] = useState<HocPhanOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<HocPhanOption | null>(null);
  const [deletingSubject, setDeletingSubject] = useState<HocPhanOption | null>(null);
  const [form, setForm] = useState<SubjectForm>(emptyForm);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profile, subjectData] = await Promise.all([
        AdminService.getProfile(),
        AdminService.getSubjects(),
      ]);
      setUser(profile);
      setSubjects(subjectData);
    } catch (err) {
      console.error("Không thể tải danh sách học phần:", err);
      setError("Không thể tải danh sách học phần.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredSubjects = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return subjects;

    return subjects.filter((subject) => {
      return (
        subject.course_id.toString().includes(keyword) ||
        subject.course_name.toLowerCase().includes(keyword) ||
        (subject.description || "").toLowerCase().includes(keyword)
      );
    });
  }, [query, subjects]);

  const openCreateDialog = () => {
    setEditingSubject(null);
    setForm(emptyForm);
    setDialogOpen(true);
  };

  const openEditDialog = (subject: HocPhanOption) => {
    setEditingSubject(subject);
    setForm({
      course_id: subject.course_id.toString(),
      course_name: subject.course_name,
      credit_count: (subject.credit_count ?? 3).toString(),
      description: subject.description || "",
      status: subject.status === false ? "false" : "true",
    });
    setDialogOpen(true);
  };

  const submitForm = async () => {
    const subjectId = Number(form.course_id);
    const credits = Number(form.credit_count);
    if (!subjectId || !form.course_name.trim() || !credits) {
      setError("Vui lòng nhập đầy đủ mã học phần, tên học phần và số tín chỉ.");
      return;
    }

    setSubmitting(true);
    setError(null);
    const payload = {
      course_name: form.course_name.trim(),
      credit_count: credits,
      description: form.description.trim() || null,
      status: form.status === "true",
    };

    try {
      if (editingSubject) {
        await AdminService.updateSubject(editingSubject.course_id, payload);
      } else {
        await AdminService.createSubject({
          course_id: subjectId,
          ...payload,
        });
      }
      setDialogOpen(false);
      await loadData();
    } catch (err) {
      console.error("Không thể lưu học phần:", err);
      setError("Không thể lưu học phần. Vui lòng kiểm tra lại dữ liệu.");
    } finally {
      setSubmitting(false);
    }
  };

  const confirmDelete = (subject: HocPhanOption) => {
    setDeletingSubject(subject);
    setDeleteOpen(true);
  };

  const deleteSubject = async () => {
    if (!deletingSubject) return;

    setSubmitting(true);
    setError(null);
    try {
      await AdminService.deleteSubject(deletingSubject.course_id);
      setDeleteOpen(false);
      setDeletingSubject(null);
      await loadData();
    } catch (err) {
      console.error("Không thể xóa học phần:", err);
      setError("Không thể xóa học phần này. Có thể học phần đang được gán cho các lớp học.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell role="admin" user={user} breadcrumb="Quản lý học phần">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-[#0F172A]">Học phần</h2>
            <p className="mt-1 text-sm text-[#64748B]">
              Quản lý danh mục học phần dùng cho các lớp học phần và đăng ký giảng dạy.
            </p>
          </div>
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white">
            <Plus className="mr-2 h-4 w-4" />
            Thêm học phần
          </Button>
        </div>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <Card className="border-[#E2E8F0] shadow-sm">
          <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="flex items-center gap-2 text-base text-[#0F172A] font-bold">
              <BookOpen className="h-5 w-5 text-[#0EA5E9]" />
              Danh sách học phần
            </CardTitle>
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
              <Input
                className="pl-9 border-[#E2E8F0]"
                placeholder="Tìm theo mã, tên học phần, mô tả..."
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-xl border border-[#E2E8F0]">
              <table className="w-full text-sm text-left">
                <thead className="bg-[#F8FAFC] text-left text-xs font-semibold uppercase tracking-wide text-[#475569] border-b border-[#E2E8F0]">
                  <tr>
                    <th className="px-6 py-4">Mã học phần</th>
                    <th className="px-6 py-4">Tên học phần</th>
                    <th className="px-6 py-4">Tín chỉ</th>
                    <th className="px-6 py-4">Trạng thái</th>
                    <th className="px-6 py-4 text-right">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-[#64748B]">
                        Đang tải dữ liệu...
                      </td>
                    </tr>
                  ) : filteredSubjects.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-[#64748B]">
                        Chưa có học phần phù hợp.
                      </td>
                    </tr>
                  ) : (
                    filteredSubjects.map((subject) => (
                      <tr key={subject.course_id} className="bg-white hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 font-bold text-[#0F172A]">HP{subject.course_id}</td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-[#0F172A]">{subject.course_name}</div>
                          {subject.description && (
                            <div className="mt-1 line-clamp-1 text-xs text-[#64748B]">{subject.description}</div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-slate-700 font-semibold">{subject.credit_count ?? "-"} tín chỉ</td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                              subject.status === false
                                ? "bg-slate-100 text-slate-500 border-slate-200"
                                : "bg-[#E8F5E9] text-[#22C55E] border-[#22C55E]/15"
                            }`}
                          >
                            {subject.status === false ? "Tạm dừng" : "Hoạt động"}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="icon" onClick={() => openEditDialog(subject)} className="h-8 w-8 text-[#0EA5E9] hover:bg-sky-50">
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => confirmDelete(subject)} className="h-8 w-8 text-[#EF4444] hover:bg-rose-50">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle className="text-[#0F172A] font-bold text-lg">
              {editingSubject ? "Cập nhật học phần" : "Thêm học phần mới"}
            </DialogTitle>
            <DialogDescription>
              Nhập thông tin chi tiết học phần trong chương trình đào tạo.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="subject-id" className="text-[#0F172A] font-semibold">Mã học phần</Label>
              <Input
                id="subject-id"
                type="number"
                min="1"
                disabled={Boolean(editingSubject)}
                value={form.course_id}
                onChange={(event) => setForm((prev) => ({ ...prev, course_id: event.target.value }))}
                className="border-[#E2E8F0]"
                placeholder="Ví dụ: 101"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-name" className="text-[#0F172A] font-semibold">Tên học phần</Label>
              <Input
                id="subject-name"
                value={form.course_name}
                onChange={(event) => setForm((prev) => ({ ...prev, course_name: event.target.value }))}
                className="border-[#E2E8F0]"
                placeholder="Ví dụ: Cấu trúc dữ liệu và giải thuật"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-credit" className="text-[#0F172A] font-semibold">Số tín chỉ</Label>
              <Input
                id="subject-credit"
                type="number"
                min="1"
                value={form.credit_count}
                onChange={(event) => setForm((prev) => ({ ...prev, credit_count: event.target.value }))}
                className="border-[#E2E8F0]"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-status" className="text-[#0F172A] font-semibold">Trạng thái</Label>
              <Select
                value={form.status}
                onValueChange={(value) => setForm((prev) => ({ ...prev, status: value }))}
              >
                <SelectTrigger id="subject-status" className="border-[#E2E8F0]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Hoạt động</SelectItem>
                  <SelectItem value="false">Tạm dừng</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-description" className="text-[#0F172A] font-semibold">Mô tả</Label>
              <Textarea
                id="subject-description"
                value={form.description}
                onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
                className="border-[#E2E8F0] min-h-[80px]"
                placeholder="Mô tả tóm tắt nội dung học phần..."
              />
            </div>
          </div>
          <DialogFooter className="pt-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={submitting} className="border-[#E2E8F0] text-slate-600">
              Hủy
            </Button>
            <Button onClick={submitForm} disabled={submitting} className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white">
              {submitting ? "Đang lưu..." : "Lưu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle className="text-[#EF4444] font-bold text-lg">Xóa học phần</DialogTitle>
            <DialogDescription className="pt-1">
              Bạn có chắc chắn muốn xóa học phần <span className="font-semibold text-slate-900">{deletingSubject?.course_name}</span>? Thao tác này không thể hoàn tác.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setDeleteOpen(false)} disabled={submitting} className="border-[#E2E8F0] text-slate-600">
              Hủy
            </Button>
            <Button variant="destructive" onClick={deleteSubject} disabled={submitting} className="bg-[#EF4444] hover:bg-[#DC2626] text-white">
              {submitting ? "Đang xóa..." : "Xóa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
