import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export const ClassService = {
  getClasses: async (): Promise<CourseClass[]> => {
    try {
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
      console.warn("Lỗi tải lớp học phần từ API, thử lại sau.", error);
      throw error;
    }
  }
};
