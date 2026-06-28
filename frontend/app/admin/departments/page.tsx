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
      console.error("Khong the tai danh sach major:", err);
      setError("Khong the tai danh sach major.");
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
      setError("Vui long nhap first_name major.");
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
      console.error("Khong the luu major:", err);
      setError("Khong the luu major. Vui long kiem tra du lieu.");
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
      console.error("Khong the xoa major:", err);
      setError("Khong the xoa major. Co the major dang duoc su dung.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell role="admin" user={user} breadcrumb="Quan ly major">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-[#0F172A]">Major dao tao</h2>
            <p className="mt-1 text-sm text-[#64748B]">
              Quan ly danh muc major de phan loai sinh vien va chuong trinh hoc.
            </p>
          </div>
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C]">
            <Plus className="mr-2 h-4 w-4" />
            Them major
          </Button>
        </div>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <Card>
          <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-[#0EA5E9]" />
              Danh sach major
            </CardTitle>
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
              <Input
                className="pl-9"
                placeholder="Tim theo ma, first_name, mo ta"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-md border border-[#E2E8F0]">
              <table className="w-full text-sm">
                <thead className="bg-[#F8FAFC] text-left text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-4 py-3">Ma</th>
                    <th className="px-4 py-3">Ten major</th>
                    <th className="px-4 py-3 text-right">Thao tac</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {loading ? (
                    <tr>
                      <td colSpan={3} className="px-4 py-8 text-center text-[#64748B]">
                        Dang tai du lieu...
                      </td>
                    </tr>
                  ) : filteredDepartments.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="px-4 py-8 text-center text-[#64748B]">
                        Chua co major phu hop.
                      </td>
                    </tr>
                  ) : (
                    filteredDepartments.map((department) => (
                      <tr key={department.major_id} className="bg-white">
                        <td className="px-4 py-3 font-medium text-[#0F172A]">{department.major_id}</td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-[#0F172A]">{department.major_name}</div>
                          {department.description && (
                            <div className="mt-1 line-clamp-1 text-xs text-[#64748B]">{department.description}</div>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="icon" onClick={() => openEditDialog(department)}>
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => confirmDelete(department)}>
                              <Trash2 className="h-4 w-4 text-red-600" />
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingDepartment ? "Cap nhat major" : "Them major"}</DialogTitle>
            <DialogDescription>Nhap thong tin major dao tao.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="department-name">Ten major</Label>
              <Input
                id="department-name"
                value={form.major_name}
                onChange={(event) => setForm((prev) => ({ ...prev, major_name: event.target.value }))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="department-description">Mo ta</Label>
              <Textarea
                id="department-description"
                value={form.description}
                onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={submitting}>
              Huy
            </Button>
            <Button onClick={submitForm} disabled={submitting}>
              {submitting ? "Dang luu..." : "Luu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xoa major</DialogTitle>
            <DialogDescription>
              Ban co chac muon xoa major {deletingDepartment?.major_name}? Thao tac nay khong the hoan tac.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)} disabled={submitting}>
              Huy
            </Button>
            <Button variant="destructive" onClick={deleteDepartment} disabled={submitting}>
              {submitting ? "Dang xoa..." : "Xoa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
