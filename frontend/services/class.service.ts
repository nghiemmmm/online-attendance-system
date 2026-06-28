import { CourseClass } from "@/types/class";
import { apiClient } from "@/lib/api-client";

export const ClassService = {
  getClasses: async (): Promise<CourseClass[]> => {
    try {
      const response = await apiClient.get<any>("/staff/me/class-sections");
      const classes = response.data || [];
      return classes.map((c: any) => ({
        id: c.class_section_id,
        maLop: c.course_id?.toString() || "",
        tenHocPhan: c.course_name || "Lớp học phần",
        giangVien: "", // This is the lecturer themselves, can be blank or custom
        hocKy: `Học kỳ ${c.semester} - Năm học ${c.academic_year}`,
        siSo: 50, // Standard capacity or static for now since DB does not have max size
        siSoHienTai: c.current_students || 0,
        trangThai: c.status ? "Đang học" : "Đã kết thúc",
      }));
    } catch (error) {
      console.warn("Lỗi tải lớp học phần của tôi từ API.", error);
      throw error;
    }
  }
};
