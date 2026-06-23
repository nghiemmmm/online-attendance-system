import { Claim, AttendanceReport } from "@/types/lecturer";
import { apiClient } from "@/lib/api-client";

export const LecturerService = {
  getClaims: async (): Promise<Claim[]> => {
    try {
      const response = await apiClient.get<any>("/khieunai/");
      const claims = response.data || [];
      return claims.map((claim: any) => ({
        id: claim.ma_khieu_nai?.toString() || `CLM${Math.random()}`,
        studentId: claim.ma_sinh_vien?.toString() || "Unknown",
        studentName: claim.ten_sinh_vien || "Unknown",
        subjectClass: claim.ma_lop_hoc_phan?.toString() || "Unknown",
        date: claim.ngay_khieu_nai ? new Date(claim.ngay_khieu_nai).toLocaleDateString("vi-VN") : "N/A",
        reason: claim.ly_do || "",
        status: claim.trang_thai === 'cho_xu_ly' ? 'pending' : (claim.trang_thai === 'da_chap_nhan' ? 'approved' : 'rejected'),
        submittedAt: claim.ngay_khieu_nai ? new Date(claim.ngay_khieu_nai).toLocaleString("vi-VN") : "N/A",
      }));
    } catch (error) {
      console.error("Lỗi tải danh sách khiếu nại:", error);
      throw error;
    }
  },

  getReports: async (): Promise<AttendanceReport[]> => {
    try {
      // Giả sử có một API tổng hợp hoặc lấy danh sách điểm danh
      const response = await apiClient.get<any>("/lophocphan/"); // Endpoint cần thay đổi cho phù hợp
      return []; // Implement properly when API matches
    } catch (error) {
      console.error("Lỗi tải báo cáo:", error);
      throw error;
    }
  },

  updateClaimStatus: async (claimId: string, status: 'approved' | 'rejected'): Promise<boolean> => {
    try {
      const backendStatus = status === 'approved' ? 'da_chap_nhan' : 'tu_choi';
      await apiClient.patch(`/khieunai/${claimId}/status`, { trang_thai: backendStatus });
      return true;
    } catch (error) {
      console.error("Lỗi cập nhật trạng thái khiếu nại:", error);
      return false;
    }
  }
};
