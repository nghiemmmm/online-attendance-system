import { StudentProfile, StudentClaim } from "@/types/student";

export const mockProfile: StudentProfile = {
  id: "USR_SV001",
  name: "Nguyễn Tuấn A",
  studentId: "SV20210001",
  email: "tuan.a@student.edu.vn",
  phone: "0987654321",
  department: "Khoa Công nghệ Thông tin",
  faceRegistered: true,
  registeredFacesCount: 5,
};

export const mockStudentClaims: StudentClaim[] = [
  {
    id: "CLM001",
    subjectCode: "CS101",
    subjectName: "Lập trình Web",
    date: "26/05/2026",
    sessionNumber: 8,
    currentStatus: "absent",
    reason: "Camera không nhận diện được do em đeo khẩu trang",
    status: "pending",
    submittedAt: "26/05/2026 10:30"
  },
  {
    id: "CLM002",
    subjectCode: "CS201",
    subjectName: "Cơ sở dữ liệu",
    date: "20/05/2026",
    sessionNumber: 5,
    currentStatus: "late",
    reason: "Em đến trễ 5 phút do sự cố mạng ở nhà, không kịp vào Google Meet điểm danh lúc đầu giờ.",
    status: "rejected",
    submittedAt: "20/05/2026 15:00"
  },
  {
    id: "CLM003",
    subjectCode: "CS101",
    subjectName: "Lập trình Web",
    date: "15/05/2026",
    sessionNumber: 4,
    currentStatus: "absent",
    reason: "Em có giấy xin phép nghỉ ốm đã nộp cho Phòng Đào tạo.",
    status: "approved",
    submittedAt: "16/05/2026 09:15"
  }
];
