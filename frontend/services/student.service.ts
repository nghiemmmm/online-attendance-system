import { StudentProfile, StudentClaim } from "@/types/student";
import { apiClient } from "@/lib/api-client";

export const StudentService = {
  getProfile: async (): Promise<StudentProfile> => {
    try {
      const data = await apiClient.get<any>("/users/me/profile");
      const profile = data.profile || {};
      
      // Map backend response to frontend StudentProfile interface
      return {
        id: profile.ma_sinh_vien?.toString() || data.tai_khoan?.ma_tai_khoan?.toString() || "unknown",
        name: `${profile.ho || ''} ${profile.ten || ''}`.trim() || data.tai_khoan?.ten_dang_nhap || "Unknown Student",
        studentId: profile.ma_sinh_vien?.toString() || "N/A",
        email: profile.google_email || "Not provided",
        phone: profile.dien_thoai || "Not provided",
        department: profile.ma_nganh?.toString() || "Unknown Department", // Ideally we'd map this to a string name
        faceRegistered: !!profile.face_registered,
        registeredFacesCount: profile.registered_faces_count || 0,
      };
    } catch (error) {
      console.error("Error fetching student profile:", error);
      throw error;
    }
  },

  updateProfile: async (data: Partial<StudentProfile>): Promise<boolean> => {
    try {
      // Map frontend update to backend SinhVienUpdate
      const nameParts = data.name ? data.name.split(" ") : [];
      const ho = nameParts.length > 1 ? nameParts.slice(0, -1).join(" ") : undefined;
      const ten = nameParts.length > 0 ? nameParts[nameParts.length - 1] : undefined;

      const payload: any = {};
      if (ho !== undefined) payload.ho = ho;
      if (ten !== undefined) payload.ten = ten;
      if (data.email) payload.google_email = data.email;
      if (data.phone) payload.dien_thoai = data.phone;

      // Assuming there's a PATCH endpoint for student profile, adjust if different
      await apiClient.patch("/users/me/profile", payload);
      return true;
    } catch (error) {
      console.error("Error updating profile:", error);
      return false;
    }
  },

  getClaims: async (): Promise<StudentClaim[]> => {
    try {
      const response = await apiClient.get<any>("/khieu-nai");
      const claims = response?.data || [];
      
      return claims.map((claim: any) => ({
        id: claim.ma_khieu_nai?.toString() || `CLM-${Math.random().toString(36).substring(7)}`,
        subjectCode: claim.ma_lop_hoc_phan?.toString() || "Unknown",
        subjectName: "Lớp học phần " + (claim.ma_lop_hoc_phan || "Unknown"), // Needs join with lophocphan
        date: claim.ngay_khieu_nai ? new Date(claim.ngay_khieu_nai).toLocaleDateString("vi-VN") : "N/A",
        sessionNumber: 1, // Add if available in backend
        currentStatus: "absent", // Derive from attendance status
        reason: claim.ly_do || "No reason",
        status: claim.trang_thai === "DA_XU_LY" ? "approved" : claim.trang_thai === "TU_CHOI" ? "rejected" : "pending",
        submittedAt: claim.ngay_khieu_nai ? new Date(claim.ngay_khieu_nai).toLocaleString("vi-VN") : "N/A"
      }));
    } catch (error) {
      console.error("Error fetching claims:", error);
      return []; // Return empty array instead of throwing to prevent frontend crashes
    }
  },

  submitClaim: async (data: any): Promise<StudentClaim> => {
    try {
      const payload = {
        ly_do: data.reason,
        ma_diem_danh: data.ma_diem_danh || 1, // You will need the actual attendance record ID
        minh_chung: "string" // Add file upload logic if necessary
      };
      
      const claim = await apiClient.post<any>("/khieu-nai", payload);
      
      return {
        id: claim.ma_khieu_nai?.toString() || `CLM-${Math.random()}`,
        subjectCode: claim.ma_lop_hoc_phan?.toString() || data.subjectCode || "Unknown",
        subjectName: data.subjectName || "Unknown Subject",
        date: new Date().toLocaleDateString("vi-VN"),
        sessionNumber: data.sessionNumber || 1,
        currentStatus: data.currentStatus || "absent",
        reason: claim.ly_do,
        status: 'pending',
        submittedAt: new Date().toLocaleString("vi-VN")
      };
    } catch (error) {
      console.error("Error submitting claim:", error);
      throw error;
    }
  },

  verifyFace: async (file: Blob, maBuoiHoc?: number): Promise<{ verified: boolean, confidence: number, message: string }> => {
    const formData = new FormData();
    formData.append("file", file, "frame.jpg");
    if (maBuoiHoc !== undefined && maBuoiHoc !== null) {
      formData.append("ma_buoi_hoc", maBuoiHoc.toString());
    }
    
    try {
      const response = await apiClient.post<any>("/anh-khuon-mat/xac-minh-truc-tiep", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      return {
        verified: response.verified,
        confidence: response.confidence || 0,
        message: response.message || ""
      };
    } catch (error: any) {
      console.error("Error verifying face:", error);
      return {
        verified: false,
        confidence: 0,
        message: error?.response?.data?.detail || "Lỗi kết nối máy chủ"
      };
    }
  },

  getSchedule: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/sinh-vien/me/lich-hoc");
      return response.data || [];
    } catch (error) {
      console.error("Error fetching schedule:", error);
      return [];
    }
  },

  getAttendance: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/sinh-vien/me/diem-danh");
      return response.data || [];
    } catch (error) {
      console.error("Error fetching attendance:", error);
      return [];
    }
  },

  getAvailableClasses: async (): Promise<any[]> => {
    try {
      const response = await apiClient.get<any>("/sinh-vien/me/lop-hoc-phan-available");
      return response.data || [];
    } catch (error) {
      console.error("Error fetching available classes:", error);
      return [];
    }
  },

  registerClass: async (maLopHocPhan: number): Promise<boolean> => {
    try {
      await apiClient.post(`/sinh-vien/me/dang-ky-hoc-phan?ma_lop_hoc_phan=${maLopHocPhan}`, {});
      return true;
    } catch (error) {
      console.error("Error registering class:", error);
      return false;
    }
  },

  cancelClassRegistration: async (maLopHocPhan: number): Promise<boolean> => {
    try {
      await apiClient.delete(`/sinh-vien/me/huy-dang-ky-hoc-phan/${maLopHocPhan}`);
      return true;
    } catch (error) {
      console.error("Error cancelling class registration:", error);
      return false;
    }
  }
};
