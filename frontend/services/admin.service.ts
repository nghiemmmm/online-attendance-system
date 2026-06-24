import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export interface HocPhanOption {
  ma_hoc_phan: number;
  ten_hoc_phan: string;
  mo_ta?: string | null;
  so_tin_chi?: number | null;
  trang_thai?: boolean;
}

export interface CanBoOption {
  ma_can_bo: number;
  ho: string;
  ten: string;
  google_email?: string | null;
  chuc_vu?: string | null;
  trang_thai?: boolean;
}

export interface NganhOption {
  ma_nganh: number;
  ten_nganh: string;
  mo_ta?: string | null;
}

export interface AdminClassPayload {
  ma_hoc_phan: number;
  ma_can_bo: number;
  hoc_ky: number;
  nam_hoc: string;
  ty_le_chuyen_can_toi_thieu: number;
  trang_thai: boolean;
}

type EnrichedClass = CourseClass & {
  maHocPhan: number;
  maCanBo: number;
  hocKyNumber: number;
  namHoc: string;
  tyLeChuyenCanToiThieu: number;
};

const formatClass = (
  item: any,
  subjects: HocPhanOption[] = [],
  lecturers: CanBoOption[] = []
): EnrichedClass => {
  const subject = subjects.find((s) => s.ma_hoc_phan === item.ma_hoc_phan);
  const lecturer = lecturers.find((l) => l.ma_can_bo === item.ma_can_bo);

  return {
    id: item.ma_lop_hoc_phan || item.id,
    maLop: item.ma_lop_hoc_phan?.toString() || item.ma_hoc_phan?.toString() || "",
    tenHocPhan: subject?.ten_hoc_phan || item.ten_hoc_phan || `Hoc phan ${item.ma_hoc_phan}`,
    giangVien: lecturer ? `${lecturer.ho} ${lecturer.ten}`.trim() : "Chua phan cong",
    hocKy: `Hoc ky ${item.hoc_ky || ""} - Nam hoc ${item.nam_hoc || ""}`,
    siSo: 50,
    siSoHienTai: item.si_so_hien_tai || 0,
    trangThai: item.trang_thai ? "Đang học" : "Đã kết thúc",
    maHocPhan: item.ma_hoc_phan,
    maCanBo: item.ma_can_bo,
    hocKyNumber: item.hoc_ky || 1,
    namHoc: item.nam_hoc || "",
    tyLeChuyenCanToiThieu: item.ty_le_chuyen_can_toi_thieu ?? 0.8,
  };
};

export const AdminService = {
  getClasses: async (): Promise<EnrichedClass[]> => {
    try {
      const [response, subjects, lecturers] = await Promise.all([
        apiClient.get<any>("/lop-hoc-phan/"),
        AdminService.getSubjects(),
        AdminService.getLecturers(),
      ]);
      return (response.data || []).map((item: any) => formatClass(item, subjects, lecturers));
    } catch (error) {
      console.warn("Loi khi lay du lieu lop hoc phan tu backend:", error);
      return [];
    }
  },

  createClass: async (data: AdminClassPayload): Promise<EnrichedClass> => {
    const response = await apiClient.post<any>("/lop-hoc-phan/", data);
    const [subjects, lecturers] = await Promise.all([
      AdminService.getSubjects(),
      AdminService.getLecturers(),
    ]);
    return formatClass(response, subjects, lecturers);
  },

  updateClass: async (id: number, data: Partial<AdminClassPayload>): Promise<EnrichedClass> => {
    const response = await apiClient.patch<any>(`/lop-hoc-phan/${id}`, data);
    const [subjects, lecturers] = await Promise.all([
      AdminService.getSubjects(),
      AdminService.getLecturers(),
    ]);
    return formatClass(response, subjects, lecturers);
  },

  deleteClass: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/lop-hoc-phan/${id}`);
    return true;
  },

  getSubjects: async (): Promise<HocPhanOption[]> => {
    const response = await apiClient.get<any>("/hocphan/");
    return response.data || [];
  },

  createSubject: async (payload: any): Promise<HocPhanOption> => {
    return apiClient.post<HocPhanOption>("/hocphan/", payload);
  },

  updateSubject: async (maHocPhan: number, payload: any): Promise<HocPhanOption> => {
    return apiClient.patch<HocPhanOption>(`/hocphan/${maHocPhan}`, payload);
  },

  deleteSubject: async (maHocPhan: number): Promise<boolean> => {
    await apiClient.delete(`/hocphan/${maHocPhan}`);
    return true;
  },

  getDepartments: async (): Promise<NganhOption[]> => {
    const response = await apiClient.get<any>("/nganh/");
    return response.data || [];
  },

  createDepartment: async (payload: any): Promise<NganhOption> => {
    return apiClient.post<NganhOption>("/nganh/", payload);
  },

  updateDepartment: async (maNganh: number, payload: any): Promise<NganhOption> => {
    return apiClient.patch<NganhOption>(`/nganh/${maNganh}`, payload);
  },

  deleteDepartment: async (maNganh: number): Promise<boolean> => {
    await apiClient.delete(`/nganh/${maNganh}`);
    return true;
  },

  getLecturers: async (): Promise<CanBoOption[]> => {
    const response = await apiClient.get<any>("/canbo/?limit=200");
    return (response.data || []).filter((item: CanBoOption) => item.trang_thai !== false);
  },

  registerFace: async (studentId: number | string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("ma_sinh_vien", studentId.toString());
    formData.append("file", file);

    return apiClient.post<any>("/anh-khuon-mat/admin/dang-ky", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  getStats: async (): Promise<any> => {
    try {
      return await apiClient.get<any>("/he-thong/stats");
    } catch (error) {
      console.error("Loi khi lay so lieu thong ke he thong:", error);
      throw error;
    }
  },

  getLogs: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/he-thong/logs");
      return response || [];
    } catch (error) {
      console.error("Loi khi lay nhat ky hoat dong:", error);
      return [];
    }
  },

  getUsers: async (role: string, status: string, q: string): Promise<any> => {
    const queryParts: string[] = [];
    if (role && role !== "all") queryParts.push(`role=${role}`);
    if (status && status !== "all") queryParts.push(`status=${status}`);
    if (q) queryParts.push(`q=${encodeURIComponent(q)}`);

    const queryString = queryParts.length > 0 ? `?${queryParts.join("&")}` : "";
    return apiClient.get<any>(`/users/profiles${queryString}`);
  },

  createUser: async (user: any): Promise<any> => {
    return apiClient.post<any>("/users/with-profile", user);
  },

  toggleUserStatus: async (accountId: number): Promise<any> => {
    return apiClient.patch<any>(`/users/${accountId}/toggle-status`, {});
  },

  deleteUser: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/users/${id}`);
    return true;
  },

  getProfile: async (): Promise<{ name: string; email: string }> => {
    const data = await apiClient.get<any>("/users/me/profile");
    return {
      name: data.tai_khoan?.ten_dang_nhap?.split("@")[0] || "Quan tri vien",
      email: data.tai_khoan?.ten_dang_nhap || "admin@university.edu.vn",
    };
  },

  getReportStats: async (): Promise<any> => {
    return apiClient.get<any>("/he-thong/reports");
  },
};
