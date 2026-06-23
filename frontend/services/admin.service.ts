import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

// This is a placeholder structure for when backend implements /lophocphan fully
export const AdminService = {
  getClasses: async (): Promise<CourseClass[]> => {
    try {
      // Trying to fetch from backend
      const response = await apiClient.get<any>("/lophocphan/");
      const classes = response.data || [];
      return classes.map((c: any) => ({
        id: c.ma_lop_hoc_phan || c.id,
        maLop: c.ma_lop_hoc_phan?.toString() || c.maLop,
        tenLop: c.ten_lop_hoc_phan || c.tenLop,
        giangVien: c.ten_giang_vien || c.giangVien || "Chưa phân công",
        siSo: c.si_so || c.siSo || 0,
        siSoHienTai: c.si_so_hien_tai || c.siSoHienTai || 0,
        phongHoc: c.phong_hoc || c.phongHoc || "Chưa xếp",
        trangThai: c.trang_thai === "active" ? "active" : "completed",
        lichHoc: c.lich_hoc || "Chưa có"
      }));
    } catch (error) {
      console.warn("Lỗi khi lấy dữ liệu từ backend, trả về mock data:", error);
      // Fallback or throw error depending on requirements
      return [];
    }
  },

  createClass: async (data: Omit<CourseClass, 'id' | 'siSoHienTai'>): Promise<CourseClass> => {
    const payload = {
      ten_lop_hoc_phan: data.tenLop,
      si_so: data.siSo,
      phong_hoc: data.phongHoc,
      trang_thai: data.trangThai,
    };
    const response = await apiClient.post<any>("/lophocphan/", payload);
    return {
      id: response.ma_lop_hoc_phan || Date.now(),
      maLop: response.ma_lop_hoc_phan?.toString() || data.maLop,
      tenLop: response.ten_lop_hoc_phan || data.tenLop,
      giangVien: data.giangVien,
      siSo: data.siSo,
      siSoHienTai: data.siSo, 
      phongHoc: data.phongHoc,
      trangThai: data.trangThai,
      lichHoc: data.lichHoc
    };
  },

  updateClass: async (id: number, data: Partial<CourseClass>): Promise<CourseClass> => {
    const payload: any = {};
    if (data.tenLop) payload.ten_lop_hoc_phan = data.tenLop;
    if (data.siSo) payload.si_so = data.siSo;
    if (data.phongHoc) payload.phong_hoc = data.phongHoc;
    
    const response = await apiClient.patch<any>(`/lophocphan/${id}`, payload);
    return response;
  },

  deleteClass: async (id: number): Promise<boolean> => {
    await apiClient.delete(`/lophocphan/${id}`);
    return true;
  },

  registerFace: async (studentId: number | string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("ma_sinh_vien", studentId.toString());
    formData.append("file", file);
    
    // apiClient.post by default uses application/json if we pass object. 
    // For FormData we need to let browser set Content-Type to multipart/form-data with boundary.
    const response = await apiClient.post<any>("/anh-khuon-mat/admin/dang-ky", formData, {
      headers: {
        "Content-Type": "multipart/form-data" // Axios might handle this automatically, but keeping it explicit or omitting might be needed based on apiClient implementation. Actually, axios strips it if not properly formatted. Let's just pass formData.
      }
    });
    return response;
  }
};
