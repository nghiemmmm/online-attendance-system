import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export interface HocPhanOption {
  course_id: number;
  course_name: string;
  description?: string | null;
  credit_count?: number | null;
  status?: boolean;
}

export interface CanBoOption {
  staff_id: number;
  last_name: string;
  first_name: string;
  google_email?: string | null;
  position?: string | null;
  status?: boolean;
}

export interface NganhOption {
  major_id: number;
  major_name: string;
  description?: string | null;
}

export interface AdminClassPayload {
  course_id: number;
  staff_id: number;
  semester: number;
  academic_year: string;
  minimum_attendance_rate: number;
  status: boolean;
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
  const subject = subjects.find((s) => s.course_id === item.course_id);
  const lecturer = lecturers.find((l) => l.staff_id === item.staff_id);

  return {
    id: item.class_section_id || item.id,
    maLop: item.class_section_id?.toString() || item.course_id?.toString() || "",
    tenHocPhan: subject?.course_name || item.course_name || `Hoc phan ${item.course_id}`,
    giangVien: lecturer ? `${lecturer.last_name} ${lecturer.first_name}`.trim() : "Chua phan cong",
    hocKy: `Hoc ky ${item.semester || ""} - Nam hoc ${item.academic_year || ""}`,
    siSo: 50,
    siSoHienTai: item.current_students || 0,
    trangThai: item.status ? "Đang học" : "Đã kết thúc",
    maHocPhan: item.course_id,
    maCanBo: item.staff_id,
    hocKyNumber: item.semester || 1,
    namHoc: item.academic_year || "",
    tyLeChuyenCanToiThieu: item.minimum_attendance_rate ?? 0.8,
  };
};

export const AdminService = {
  getClasses: async (): Promise<EnrichedClass[]> => {
    try {
      const [response, subjects, lecturers] = await Promise.all([
        apiClient.get<any>("/class-sections/"),
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
    const response = await apiClient.post<any>("/class-sections/", data);
    const [subjects, lecturers] = await Promise.all([
      AdminService.getSubjects(),
      AdminService.getLecturers(),
    ]);
    return formatClass(response, subjects, lecturers);
  },

  updateClass: async (id: number, data: Partial<AdminClassPayload>): Promise<EnrichedClass> => {
    const response = await apiClient.patch<any>(`/class-sections/${id}`, data);
    const [subjects, lecturers] = await Promise.all([
      AdminService.getSubjects(),
      AdminService.getLecturers(),
    ]);
    return formatClass(response, subjects, lecturers);
  },

  deleteClass: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/class-sections/${id}`);
    return true;
  },

  getSubjects: async (): Promise<HocPhanOption[]> => {
    const response = await apiClient.get<any>("/courses/");
    return response.data || [];
  },

  createSubject: async (payload: any): Promise<HocPhanOption> => {
    return apiClient.post<HocPhanOption>("/courses/", payload);
  },

  updateSubject: async (maHocPhan: number, payload: any): Promise<HocPhanOption> => {
    return apiClient.patch<HocPhanOption>(`/courses/${maHocPhan}`, payload);
  },

  deleteSubject: async (maHocPhan: number): Promise<boolean> => {
    await apiClient.delete(`/courses/${maHocPhan}`);
    return true;
  },

  getDepartments: async (): Promise<NganhOption[]> => {
    const response = await apiClient.get<any>("/majors/");
    return response.data || [];
  },

  createDepartment: async (payload: any): Promise<NganhOption> => {
    return apiClient.post<NganhOption>("/majors/", payload);
  },

  updateDepartment: async (maNganh: number, payload: any): Promise<NganhOption> => {
    return apiClient.patch<NganhOption>(`/majors/${maNganh}`, payload);
  },

  deleteDepartment: async (maNganh: number): Promise<boolean> => {
    await apiClient.delete(`/majors/${maNganh}`);
    return true;
  },

  getLecturers: async (): Promise<CanBoOption[]> => {
    const response = await apiClient.get<any>("/staff/?limit=200");
    return (response.data || []).filter((item: CanBoOption) => item.status !== false);
  },

  registerFace: async (studentId: number | string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("student_id", studentId.toString());
    formData.append("file", file);

    return apiClient.post<any>("/face-images/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  getFaceRecords: async (status?: "CHO_DUYET" | "DA_DUYET" | "TU_CHOI"): Promise<any[]> => {
    try {
      const query = status ? `?review_status=${status}` : "";
      const response = await apiClient.get<any>(`/face-images/${query}`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải dữ liệu khuôn mặt:", error);
      return [];
    }
  },

  approveFace: async (faceId: number): Promise<any> => {
    return apiClient.patch<any>(`/face-images/${faceId}`, {
      review_status: "approved",
    });
  },

  rejectFace: async (faceId: number, reason: string): Promise<any> => {
    return apiClient.patch<any>(`/face-images/${faceId}`, {
      review_status: "rejected",
      rejection_reason: reason,
    });
  },

  getStats: async (): Promise<any> => {
    try {
      return await apiClient.get<any>("/system/stats");
    } catch (error) {
      console.error("Loi khi lay so lieu thong ke he thong:", error);
      throw error;
    }
  },

  getLogs: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/system/logs");
      const rows = Array.isArray(response) ? response : response?.data || [];
      return rows.map((log: any) => ({
        id: log.audit_log_id?.toString() || log.id || `${log.action}-${log.timestamp}`,
        user: log.account_id ? `TK #${log.account_id}` : "Hệ thống",
        action: log.action || log.action || "Hoạt động",
        target: log.target_id
          ? `${log.target_type || "Đối tượng"} #${log.target_id}`
          : log.target_type || log.target || "",
        time: log.timestamp ? new Date(log.timestamp).toLocaleString("vi-VN") : log.time || "",
        type:
          log.status === "FAILED"
            ? "edit"
            : log.action?.includes("DUYET")
              ? "approve"
              : log.action?.includes("DANG_NHAP")
                ? "login"
                : "edit",
        status: log.status === "FAILED" ? "error" : "success",
        details: log.detail || "",
        raw: log,
      }));
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
    return apiClient.post<any>("/users/profiles", user);
  },

  toggleUserStatus: async (accountId: number): Promise<any> => {
    return apiClient.patch<any>(`/users/${accountId}/status`, {});
  },

  deleteUser: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/users/${id}`);
    return true;
  },

  getProfile: async (): Promise<{ name: string; email: string }> => {
    const data = await apiClient.get<any>("/users/me/profile");
    return {
      name: data.account?.username?.split("@")[0] || "Quan tri vien",
      email: data.account?.username || "admin@university.edu.vn",
    };
  },

  getReportStats: async (): Promise<any> => {
    return apiClient.get<any>("/system/reports");
  },
};
