import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export const AdminService = {
  getClasses: async (): Promise<CourseClass[]> => {
    try {
      const response = await apiClient.get<any>("/lop-hoc-phan/");
      const classes = response.data || [];
      return classes.map((c: any) => ({
        id: c.ma_lop_hoc_phan || c.id,
        maLop: c.ma_hoc_phan?.toString() || "",
        tenHocPhan: c.ten_hoc_phan || "Lớp học phần",
        giangVien: c.ten_giang_vien || "Chưa phân công",
        hocKy: `Học kỳ ${c.hoc_ky} - Năm học ${c.nam_hoc}`,
        siSo: 50,
        siSoHienTai: c.si_so_hien_tai || 0,
        trangThai: c.trang_thai ? "Đang học" : "Đã kết thúc",
      }));
    } catch (error) {
      console.warn("Lỗi khi lấy dữ liệu lớp học phần từ backend:", error);
      return [];
    }
  },

  createClass: async (data: Omit<CourseClass, 'id' | 'siSoHienTai'>): Promise<CourseClass> => {
    const payload = {
      ten_lop_hoc_phan: data.tenHocPhan,
      si_so: data.siSo,
      phong_hoc: "Phòng lý thuyết",
      trang_thai: data.trangThai === "Đang học",
    };
    const response = await apiClient.post<any>("/lop-hoc-phan/", payload);
    return {
      id: response.ma_lop_hoc_phan || Date.now(),
      maLop: response.ma_lop_hoc_phan?.toString() || data.maLop,
      tenHocPhan: response.ten_hoc_phan || data.tenHocPhan,
      giangVien: data.giangVien,
      siSo: data.siSo,
      siSoHienTai: 0, 
      trangThai: data.trangThai,
      hocKy: data.hocKy || "",
    };
  },

  updateClass: async (id: number, data: Partial<CourseClass>): Promise<CourseClass> => {
    const payload: any = {};
    if (data.tenHocPhan) payload.ten_lop_hoc_phan = data.tenHocPhan;
    if (data.siSo) payload.si_so = data.siSo;
    
    const response = await apiClient.patch<any>(`/lop-hoc-phan/${id}`, payload);
    return response;
  },

  deleteClass: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/lop-hoc-phan/${id}`);
    return true;
  },

  registerFace: async (studentId: number | string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("ma_sinh_vien", studentId.toString());
    formData.append("file", file);
    
    const response = await apiClient.post<any>("/anh-khuon-mat/admin/dang-ky", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
    return response;
  },

  getStats: async (): Promise<any> => {
    try {
      const response = await apiClient.get<any>("/he-thong/stats");
      return response;
    } catch (error) {
      console.error("Lỗi khi lấy số liệu thống kê hệ thống:", error);
      throw error;
    }
  },

  getLogs: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/he-thong/logs");
      return response || [];
    } catch (error) {
      console.error("Lỗi khi lấy nhật ký hoạt động:", error);
      return [];
    }
  },

  getUsers: async (role: string, status: string, q: string): Promise<any> => {
    try {
      const queryParts: string[] = [];
      if (role && role !== "all") queryParts.push(`role=${role}`);
      if (status && status !== "all") queryParts.push(`status=${status}`);
      if (q) queryParts.push(`q=${encodeURIComponent(q)}`);
      
      const queryString = queryParts.length > 0 ? `?${queryParts.join("&")}` : "";
      const response = await apiClient.get<any>(`/users/profiles${queryString}`);
      return response;
    } catch (error) {
      console.error("Lỗi khi lấy danh sách người dùng:", error);
      throw error;
    }
  },

  createUser: async (user: any): Promise<any> => {
    try {
      const response = await apiClient.post<any>("/users/with-profile", user);
      return response;
    } catch (error) {
      console.error("Lỗi khi tạo người dùng kèm hồ sơ:", error);
      throw error;
    }
  },

  toggleUserStatus: async (accountId: number): Promise<any> => {
    try {
      const response = await apiClient.patch<any>(`/users/${accountId}/toggle-status`, {});
      return response;
    } catch (error) {
      console.error("Lỗi khi thay đổi trạng thái tài khoản:", error);
      throw error;
    }
  },

  deleteUser: async (id: number): Promise<boolean> => {
    try {
      await apiClient.delete(`/users/${id}`);
      return true;
    } catch (error) {
      console.error("Lỗi khi xóa người dùng:", error);
      throw error;
    }
  }
};
