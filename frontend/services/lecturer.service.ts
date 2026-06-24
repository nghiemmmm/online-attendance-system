import { Claim, AttendanceReport } from "@/types/lecturer";
import { apiClient } from "@/lib/api-client";

export const LecturerService = {
  getProfile: async (): Promise<{ name: string; email: string; maCanBo: number }> => {
    try {
      const data = await apiClient.get<any>("/users/me/profile");
      const profile = data.profile || {};
      return {
        name: `${profile.ho || ""} ${profile.ten || ""}`.trim() || data.tai_khoan?.ten_dang_nhap || "Giảng viên",
        email: profile.google_email || data.tai_khoan?.ten_dang_nhap || "Unknown",
        maCanBo: profile.ma_can_bo || 0,
      };
    } catch (error) {
      console.error("Lỗi tải thông tin cá nhân giảng viên:", error);
      throw error;
    }
  },

  getClaims: async (maCanBo: number): Promise<Claim[]> => {
    try {
      const response = await apiClient.get<any>(`/khieu-nai/can-bo/${maCanBo}/can-xu-ly`);
      const claims = response.data || [];
      return claims.map((claim: any) => ({
        id: claim.ma_khieu_nai?.toString() || `CLM${Math.random()}`,
        studentId: claim.ma_sinh_vien?.toString() || "Unknown",
        studentName: claim.ho_ten_sinh_vien || "Unknown",
        subjectCode: claim.ma_lop_hoc_phan?.toString() || "Unknown",
        subjectName: claim.ten_hoc_phan || "Lớp học phần",
        date: claim.ngay_hoc ? new Date(claim.ngay_hoc).toLocaleDateString("vi-VN") : "N/A",
        sessionNumber: claim.so_buoi || 0,
        currentStatus: claim.trang_thai_diem_danh === 'CO_MAT' ? 'present' : (claim.trang_thai_diem_danh === 'DI_MUON' ? 'late' : 'absent'),
        reason: claim.ly_do || "",
        status: claim.trang_thai === 'CHO_XU_LY' ? 'pending' : (claim.trang_thai === 'DA_DUYET' ? 'approved' : 'rejected'),
        submittedAt: claim.ngay_gui ? new Date(claim.ngay_gui).toLocaleString("vi-VN") : "N/A",
      }));
    } catch (error) {
      console.error("Lỗi tải danh sách khiếu nại:", error);
      throw error;
    }
  },

  getLichDayToday: async (): Promise<any[]> => {
    try {
      const todayStr = new Date().toISOString().split("T")[0];
      const response = await apiClient.get<any>(`/canbo/me/lich-day?from_date=${todayStr}&to_date=${todayStr}`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải lịch dạy hôm nay:", error);
      return [];
    }
  },

  getRecentSessions: async (maCanBo: number): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>(`/canbo/${maCanBo}/buoi-hoc/gan-day`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải các buổi học gần đây:", error);
      return [];
    }
  },

  getPendingClaimsCount: async (maCanBo: number): Promise<number> => {
    try {
      const response = await apiClient.get<any>(`/canbo/${maCanBo}/khieu-nai/cho-xu-ly/count`);
      return response.count || 0;
    } catch (error) {
      console.error("Lỗi tải số khiếu nại chờ xử lý:", error);
      return 0;
    }
  },

  getMonthlyAttendanceSummary: async (maCanBo: number): Promise<any> => {
    try {
      const response = await apiClient.get<any>(`/canbo/${maCanBo}/attendance/monthly-summary`);
      return response;
    } catch (error) {
      console.error("Lỗi tải thống kê điểm danh tháng:", error);
      return null;
    }
  },

  getLopHocPhanCount: async (maCanBo: number): Promise<number> => {
    try {
      const response = await apiClient.get<any>(`/canbo/${maCanBo}/lop-hoc-phan/dang-day/count`);
      return response.count || 0;
    } catch (error) {
      console.error("Lỗi tải số lớp học phần đang giảng dạy:", error);
      return 0;
    }
  },

  getReports: async (): Promise<AttendanceReport[]> => {
    try {
      const response = await apiClient.get<AttendanceReport[]>("/canbo/me/reports");
      return response; 
    } catch (error) {
      console.error("Lỗi tải báo cáo:", error);
      throw error;
    }
  },

  updateClaimStatus: async (maCanBo: number, claimId: string, status: 'approved' | 'rejected'): Promise<boolean> => {
    try {
      const idNum = parseInt(claimId);
      if (status === 'approved') {
        await apiClient.patch(`/khieu-nai/can-bo/${maCanBo}/can-xu-ly/${idNum}/chap-thuan`, {
          trang_thai_diem_danh_moi: "CO_MAT",
          ghi_chu_xu_ly: "Giảng viên đã chấp thuận khiếu nại"
        });
      } else {
        await apiClient.patch(`/khieu-nai/can-bo/${maCanBo}/can-xu-ly/${idNum}/tu-choi`, {
          ghi_chu_xu_ly: "Giảng viên từ chối khiếu nại"
        });
      }
      return true;
    } catch (error) {
      console.error("Lỗi cập nhật trạng thái khiếu nại:", error);
      return false;
    }
  },

  getLiveAttendance: async (maBuoiHoc: number): Promise<any[]> => {
    try {
      const response = await apiClient.get<any[]>(`/buoi-hoc/${maBuoiHoc}/diem-danh`);
      return response;
    } catch (error) {
      console.error("Lỗi lấy danh sách điểm danh trực tiếp:", error);
      throw error;
    }
  },

  moDiemDanh: async (maBuoiHoc: number): Promise<any> => {
    try {
      const response = await apiClient.post<any>(`/buoi-hoc/${maBuoiHoc}/mo-diem-danh`, {});
      return response;
    } catch (error) {
      console.error("Lỗi mở phiên điểm danh:", error);
      throw error;
    }
  },

  dongDiemDanh: async (maBuoiHoc: number): Promise<any> => {
    try {
      const response = await apiClient.post<any>(`/buoi-hoc/${maBuoiHoc}/dong-diem-danh`, {});
      return response;
    } catch (error) {
      console.error("Lỗi đóng phiên điểm danh:", error);
      throw error;
    }
  },

  updateAttendanceManual: async (maBuoiHoc: number, maSinhVien: number, status: 'present' | 'late' | 'absent'): Promise<any> => {
    try {
      const statusMap = {
        present: "CO_MAT",
        late: "DI_MUON",
        absent: "VANG"
      };
      const response = await apiClient.post<any>("/diem-danh/thu-cong", {
        ma_buoi_hoc: maBuoiHoc,
        ma_sinh_vien: maSinhVien,
        trang_thai: statusMap[status],
        ghi_chu: "Giảng viên cập nhật thủ công"
      });
      return response;
    } catch (error) {
      console.error("Lỗi cập nhật điểm danh thủ công:", error);
      throw error;
    }
  },

  getClassSessions: async (maLopHocPhan: number): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>(`/buoi-hoc/lop-hoc-phan/${maLopHocPhan}`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải danh sách buổi học:", error);
      throw error;
    }
  },

  createSession: async (payload: any): Promise<any> => {
    try {
      return await apiClient.post<any>("/buoi-hoc/", payload);
    } catch (error) {
      console.error("Lỗi tạo buổi học:", error);
      throw error;
    }
  },

  updateSession: async (maBuoiHoc: number, payload: any): Promise<any> => {
    try {
      return await apiClient.patch<any>(`/buoi-hoc/${maBuoiHoc}`, payload);
    } catch (error) {
      console.error("Lỗi cập nhật buổi học:", error);
      throw error;
    }
  },

  cancelSession: async (maBuoiHoc: number): Promise<any> => {
    try {
      return await apiClient.delete<any>(`/buoi-hoc/${maBuoiHoc}/giang-vien`);
    } catch (error) {
      console.error("Lỗi hủy buổi học:", error);
      throw error;
    }
  },

  getClassWarnings: async (maLopHocPhan: number): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>(`/lop-hoc-phan/${maLopHocPhan}/canh-bao`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải cảnh báo chuyên cần:", error);
      return [];
    }
  },

  getClassStudents: async (maLopHocPhan: number): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>(`/lop-hoc-phan/${maLopHocPhan}/sinh-vien`);
      return response.data || [];
    } catch (error) {
      console.error("Lỗi tải danh sách sinh viên lớp học phần:", error);
      return [];
    }
  },


  downloadAttendanceReport: async (maLopHocPhan: number, format: "excel" | "csv" = "excel"): Promise<void> => {
    const endpoint = format === "csv"
      ? `/bao-cao/lop-hoc-phan/${maLopHocPhan}/export-csv`
      : `/bao-cao/lop-hoc-phan/${maLopHocPhan}/export-excel`;
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:5050/api"}${endpoint}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      throw new Error("Không thể xuất báo cáo điểm danh");
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `DiemDanh_${maLopHocPhan}.${format === "csv" ? "csv" : "xlsx"}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
};
