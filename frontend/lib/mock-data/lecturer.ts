import { Claim, AttendanceReport } from "@/types/lecturer";

export const mockClaims: Claim[] = [
  {
    id: "CLM001",
    studentName: "Trần Văn C",
    studentId: "SV001",
    subjectCode: "CS101",
    subjectName: "Lập trình Web",
    date: "26/05/2026",
    sessionNumber: 8,
    currentStatus: "absent",
    reason: "Em bị ốm phải đi viện gấp nên không thể tham gia buổi học. Em có gửi kèm giấy khám bệnh.",
    proofUrl: "#",
    status: "pending",
    submittedAt: "26/05/2026 10:30"
  },
  {
    id: "CLM002",
    studentName: "Lê Thị D",
    studentId: "SV002",
    subjectCode: "CS201",
    subjectName: "Cơ sở dữ liệu",
    date: "25/05/2026",
    sessionNumber: 5,
    currentStatus: "late",
    reason: "Em có mặt lúc 13h10 do xe buýt đến trễ, nhưng camera không nhận diện được do ngược sáng.",
    status: "pending",
    submittedAt: "25/05/2026 15:00"
  },
  {
    id: "CLM003",
    studentName: "Phạm Văn E",
    studentId: "SV005",
    subjectCode: "CS101",
    subjectName: "Lập trình Web",
    date: "20/05/2026",
    sessionNumber: 7,
    currentStatus: "absent",
    reason: "Em quên điểm danh trên hệ thống.",
    status: "rejected",
    submittedAt: "20/05/2026 18:00"
  }
];

export const mockReports: AttendanceReport[] = [
  {
    id: "REP001",
    subjectCode: "CS101",
    subjectName: "Lập trình Web",
    totalSessions: 15,
    completedSessions: 8,
    totalStudents: 55,
    averageAttendanceRate: 92.5,
    dataPoints: [
      { sessionNumber: 1, date: "01/05", present: 55, absent: 0, late: 0 },
      { sessionNumber: 2, date: "04/05", present: 53, absent: 1, late: 1 },
      { sessionNumber: 3, date: "08/05", present: 54, absent: 0, late: 1 },
      { sessionNumber: 4, date: "11/05", present: 50, absent: 3, late: 2 },
      { sessionNumber: 5, date: "15/05", present: 52, absent: 2, late: 1 },
      { sessionNumber: 6, date: "18/05", present: 55, absent: 0, late: 0 },
      { sessionNumber: 7, date: "22/05", present: 48, absent: 5, late: 2 },
      { sessionNumber: 8, date: "25/05", present: 50, absent: 2, late: 3 },
    ]
  },
  {
    id: "REP002",
    subjectCode: "CS201",
    subjectName: "Cơ sở dữ liệu",
    totalSessions: 15,
    completedSessions: 5,
    totalStudents: 45,
    averageAttendanceRate: 88.0,
    dataPoints: [
      { sessionNumber: 1, date: "02/05", present: 45, absent: 0, late: 0 },
      { sessionNumber: 2, date: "09/05", present: 42, absent: 2, late: 1 },
      { sessionNumber: 3, date: "16/05", present: 40, absent: 4, late: 1 },
      { sessionNumber: 4, date: "23/05", present: 41, absent: 3, late: 1 },
      { sessionNumber: 5, date: "24/05", present: 42, absent: 1, late: 2 },
    ]
  }
];
