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
import { Textarea } from "@/components/ui/textarea";
import { AdminService, NganhOption } from "@/services/admin.service";
import { Building2, Pencil, Plus, Search, Trash2 } from "lucide-react";

type DepartmentForm = {
  major_name: string;
  description: string;
};

const emptyForm: DepartmentForm = {
  major_name: "",
  description: "",
};

export default function AdminDepartmentsPage() {
  const [user, setUser] = useState({ name: "Admin", email: "admin@university.edu.vn" });
  const [departments, setDepartments] = useState<NganhOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editingDepartment, setEditingDepartment] = useState<NganhOption | null>(null);
  const [deletingDepartment, setDeletingDepartment] = useState<NganhOption | null>(null);
  const [form, setForm] = useState<DepartmentForm>(emptyForm);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profile, departmentData] = await Promise.all([
        AdminService.getProfile(),
        AdminService.getDepartments(),
      ]);
      setUser(profile);
      setDepartments(departmentData);
    } catch (err) {
      console.error("Không thể tải danh sách ngành đào tạo:", err);
      setError("Không thể tải danh sách ngành đào tạo.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredDepartments = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return departments;

    return departments.filter((department) => {
      return (
        department.major_id.toString().includes(keyword) ||
        department.major_name.toLowerCase().includes(keyword) ||
        (department.description || "").toLowerCase().includes(keyword)
      );
    });
  }, [departments, query]);

  const openCreateDialog = () => {
    setEditingDepartment(null);
    setForm(emptyForm);
    setDialogOpen(true);
  };

  const openEditDialog = (department: NganhOption) => {
    setEditingDepartment(department);
    setForm({
      major_name: department.major_name,
      description: department.description || "",
    });
    setDialogOpen(true);
  };

  const submitForm = async () => {
    if (!form.major_name.trim()) {
      setError("Vui lòng nhập tên ngành đào tạo.");
      return;
    }

    setSubmitting(true);
    setError(null);
    const payload = {
      major_name: form.major_name.trim(),
      description: form.description.trim() || null,
    };

    try {
      if (editingDepartment) {
        await AdminService.updateDepartment(editingDepartment.major_id, payload);
      } else {
        await AdminService.createDepartment(payload);
      }
      setDialogOpen(false);
      await loadData();
    } catch (err) {
      console.error("Không thể lưu ngành đào tạo:", err);
      setError("Không thể lưu ngành đào tạo. Vui lòng kiểm tra dữ liệu.");
    } finally {
      setSubmitting(false);
    }
  };

  const confirmDelete = (department: NganhOption) => {
    setDeletingDepartment(department);
    setDeleteOpen(true);
  };

  const deleteDepartment = async () => {
    if (!deletingDepartment) return;

    setSubmitting(true);
    setError(null);
    try {
      await AdminService.deleteDepartment(deletingDepartment.major_id);
      setDeleteOpen(false);
      setDeletingDepartment(null);
      await loadData();
    } catch (err) {
      console.error("Không thể xóa ngành đào tạo:", err);
      setError("Không thể xóa ngành đào tạo. Có thể ngành đang được liên kết sử dụng.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell role="admin" user={user} breadcrumb="Quản lý ngành đào tạo">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-[#0F172A]">Ngành đào tạo</h2>
            <p className="mt-1 text-sm text-[#64748B]">
              Quản lý danh mục ngành đào tạo để phân loại sinh viên và chương trình học.
            </p>
          </div>
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C] text-white">
            <Plus className="mr-2 h-4 w-4" />
            Thêm ngành mới
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
              <Building2 className="h-5 w-5 text-[#0EA5E9]" />
              Danh sách ngành đào tạo
            </CardTitle>
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
              <Input
                className="pl-9 border-[#E2E8F0]"
                placeholder="Tìm theo mã, tên ngành, mô tả..."
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
                    <th className="px-6 py-4">Mã ngành</th>
                    <th className="px-6 py-4">Tên ngành</th>
                    <th className="px-6 py-4 text-right">Thao tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {loading ? (
                    <tr>
                      <td colSpan={3} className="px-6 py-8 text-center text-[#64748B]">
                        Đang tải dữ liệu...
                      </td>
                    </tr>
                  ) : filteredDepartments.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="px-6 py-8 text-center text-[#64748B]">
                        Chưa có ngành đào tạo phù hợp.
                      </td>
                    </tr>
                  ) : (
                    filteredDepartments.map((department) => (
                      <tr key={department.major_id} className="bg-white hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 font-bold text-[#0F172A]">MNG{department.major_id}</td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-[#0F172A]">{department.major_name}</div>
                          {department.description && (
                            <div className="mt-1 line-clamp-1 text-xs text-[#64748B]">{department.description}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="icon" onClick={() => openEditDialog(department)} className="h-8 w-8 text-[#0EA5E9] hover:bg-sky-50">
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => confirmDelete(department)} className="h-8 w-8 text-[#EF4444] hover:bg-rose-50">
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
              {editingDepartment ? "Cập nhật ngành đào tạo" : "Thêm ngành đào tạo"}
            </DialogTitle>
            <DialogDescription>
              Nhập thông tin chi tiết của ngành đào tạo mới.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="department-name" className="text-[#0F172A] font-semibold">Tên ngành</Label>
              <Input
                id="department-name"
                value={form.major_name}
                onChange={(event) => setForm((prev) => ({ ...prev, major_name: event.target.value }))}
                className="border-[#E2E8F0]"
                placeholder="Ví dụ: Công nghệ thông tin"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="department-description" className="text-[#0F172A] font-semibold">Mô tả</Label>
              <Textarea
                id="department-description"
                value={form.description}
                onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
                className="border-[#E2E8F0] min-h-[100px]"
                placeholder="Mô tả tóm tắt về ngành..."
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
            <DialogTitle className="text-[#EF4444] font-bold text-lg">Xóa ngành đào tạo</DialogTitle>
            <DialogDescription className="pt-1">
              Bạn có chắc chắn muốn xóa ngành đào tạo <span className="font-semibold text-slate-900">{deletingDepartment?.major_name}</span>? Thao tác này không thể hoàn tác.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setDeleteOpen(false)} disabled={submitting} className="border-[#E2E8F0] text-slate-600">
              Hủy
            </Button>
            <Button variant="destructive" onClick={deleteDepartment} disabled={submitting} className="bg-[#EF4444] hover:bg-[#DC2626] text-white">
              {submitting ? "Đang xóa..." : "Xóa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
