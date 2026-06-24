import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export const ClassService = {
  getClasses: async (): Promise<CourseClass[]> => {
    try {
      const response = await apiClient.get<any>("/canbo/me/lop-hoc-phan");
      const classes = response.data || [];
      return classes.map((c: any) => ({
        id: c.ma_lop_hoc_phan,
        maLop: c.ma_hoc_phan?.toString() || "",
        tenHocPhan: c.ten_hoc_phan || "Lớp học phần",
        giangVien: "", // This is the lecturer themselves, can be blank or custom
        hocKy: `Học kỳ ${c.hoc_ky} - Năm học ${c.nam_hoc}`,
        siSo: 50, // Standard capacity or static for now since DB does not have max size
        siSoHienTai: c.si_so_hien_tai || 0,
        trangThai: c.trang_thai ? "Đang học" : "Đã kết thúc",
      }));
    } catch (error) {
      console.warn("Lỗi tải lớp học phần của tôi từ API.", error);
      throw error;
    }
  }
};
