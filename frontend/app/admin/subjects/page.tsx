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
  ma_hoc_phan: string;
  ten_hoc_phan: string;
  so_tin_chi: string;
  mo_ta: string;
  trang_thai: string;
};

const emptyForm: SubjectForm = {
  ma_hoc_phan: "",
  ten_hoc_phan: "",
  so_tin_chi: "3",
  mo_ta: "",
  trang_thai: "true",
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
      console.error("Khong the tai danh sach hoc phan:", err);
      setError("Khong the tai danh sach hoc phan.");
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
        subject.ma_hoc_phan.toString().includes(keyword) ||
        subject.ten_hoc_phan.toLowerCase().includes(keyword) ||
        (subject.mo_ta || "").toLowerCase().includes(keyword)
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
      ma_hoc_phan: subject.ma_hoc_phan.toString(),
      ten_hoc_phan: subject.ten_hoc_phan,
      so_tin_chi: (subject.so_tin_chi ?? 3).toString(),
      mo_ta: subject.mo_ta || "",
      trang_thai: subject.trang_thai === false ? "false" : "true",
    });
    setDialogOpen(true);
  };

  const submitForm = async () => {
    const subjectId = Number(form.ma_hoc_phan);
    const credits = Number(form.so_tin_chi);
    if (!subjectId || !form.ten_hoc_phan.trim() || !credits) {
      setError("Vui long nhap day du ma hoc phan, ten hoc phan va so tin chi.");
      return;
    }

    setSubmitting(true);
    setError(null);
    const payload = {
      ten_hoc_phan: form.ten_hoc_phan.trim(),
      so_tin_chi: credits,
      mo_ta: form.mo_ta.trim() || null,
      trang_thai: form.trang_thai === "true",
    };

    try {
      if (editingSubject) {
        await AdminService.updateSubject(editingSubject.ma_hoc_phan, payload);
      } else {
        await AdminService.createSubject({
          ma_hoc_phan: subjectId,
          ...payload,
        });
      }
      setDialogOpen(false);
      await loadData();
    } catch (err) {
      console.error("Khong the luu hoc phan:", err);
      setError("Khong the luu hoc phan. Vui long kiem tra du lieu.");
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
      await AdminService.deleteSubject(deletingSubject.ma_hoc_phan);
      setDeleteOpen(false);
      setDeletingSubject(null);
      await loadData();
    } catch (err) {
      console.error("Khong the xoa hoc phan:", err);
      setError("Khong the xoa hoc phan. Co the hoc phan dang duoc su dung.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell role="admin" user={user} breadcrumb="Quan ly hoc phan">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-[#0F172A]">Hoc phan</h2>
            <p className="mt-1 text-sm text-[#64748B]">
              Quan ly danh muc hoc phan dung cho lop hoc phan va dang ky.
            </p>
          </div>
          <Button onClick={openCreateDialog} className="bg-[#0A2540] hover:bg-[#1A3A5C]">
            <Plus className="mr-2 h-4 w-4" />
            Them hoc phan
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
              <BookOpen className="h-5 w-5 text-[#0EA5E9]" />
              Danh sach hoc phan
            </CardTitle>
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
              <Input
                className="pl-9"
                placeholder="Tim theo ma, ten, mo ta"
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
                    <th className="px-4 py-3">Ten hoc phan</th>
                    <th className="px-4 py-3">Tin chi</th>
                    <th className="px-4 py-3">Trang thai</th>
                    <th className="px-4 py-3 text-right">Thao tac</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-[#64748B]">
                        Dang tai du lieu...
                      </td>
                    </tr>
                  ) : filteredSubjects.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-8 text-center text-[#64748B]">
                        Chua co hoc phan phu hop.
                      </td>
                    </tr>
                  ) : (
                    filteredSubjects.map((subject) => (
                      <tr key={subject.ma_hoc_phan} className="bg-white">
                        <td className="px-4 py-3 font-medium text-[#0F172A]">{subject.ma_hoc_phan}</td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-[#0F172A]">{subject.ten_hoc_phan}</div>
                          {subject.mo_ta && (
                            <div className="mt-1 line-clamp-1 text-xs text-[#64748B]">{subject.mo_ta}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-[#334155]">{subject.so_tin_chi ?? "-"}</td>
                        <td className="px-4 py-3">
                          <span
                            className={
                              subject.trang_thai === false
                                ? "inline-flex rounded-full bg-[#F1F5F9] px-2.5 py-1 text-xs font-medium text-[#475569]"
                                : "inline-flex rounded-full bg-[#DCFCE7] px-2.5 py-1 text-xs font-medium text-[#166534]"
                            }
                          >
                            {subject.trang_thai === false ? "Tam dung" : "Hoat dong"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="icon" onClick={() => openEditDialog(subject)}>
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => confirmDelete(subject)}>
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
            <DialogTitle>{editingSubject ? "Cap nhat hoc phan" : "Them hoc phan"}</DialogTitle>
            <DialogDescription>Nhap thong tin hoc phan trong chuong trinh dao tao.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="subject-id">Ma hoc phan</Label>
              <Input
                id="subject-id"
                type="number"
                min="1"
                disabled={Boolean(editingSubject)}
                value={form.ma_hoc_phan}
                onChange={(event) => setForm((prev) => ({ ...prev, ma_hoc_phan: event.target.value }))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-name">Ten hoc phan</Label>
              <Input
                id="subject-name"
                value={form.ten_hoc_phan}
                onChange={(event) => setForm((prev) => ({ ...prev, ten_hoc_phan: event.target.value }))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-credit">So tin chi</Label>
              <Input
                id="subject-credit"
                type="number"
                min="1"
                value={form.so_tin_chi}
                onChange={(event) => setForm((prev) => ({ ...prev, so_tin_chi: event.target.value }))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-status">Trang thai</Label>
              <Select
                value={form.trang_thai}
                onValueChange={(value) => setForm((prev) => ({ ...prev, trang_thai: value }))}
              >
                <SelectTrigger id="subject-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Hoat dong</SelectItem>
                  <SelectItem value="false">Tam dung</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject-description">Mo ta</Label>
              <Textarea
                id="subject-description"
                value={form.mo_ta}
                onChange={(event) => setForm((prev) => ({ ...prev, mo_ta: event.target.value }))}
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
            <DialogTitle>Xoa hoc phan</DialogTitle>
            <DialogDescription>
              Ban co chac muon xoa hoc phan {deletingSubject?.ten_hoc_phan}? Thao tac nay khong the hoan tac.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)} disabled={submitting}>
              Huy
            </Button>
            <Button variant="destructive" onClick={deleteSubject} disabled={submitting}>
              {submitting ? "Dang xoa..." : "Xoa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
