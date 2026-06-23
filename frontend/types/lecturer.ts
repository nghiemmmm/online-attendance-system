export interface Claim {
  id: string;
  studentName: string;
  studentId: string;
  subjectCode: string;
  subjectName: string;
  date: string;
  sessionNumber: number;
  currentStatus: 'absent' | 'late' | 'present';
  reason: string;
  proofUrl?: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: string;
}

export interface AttendanceReport {
  id: string;
  subjectCode: string;
  subjectName: string;
  totalSessions: number;
  completedSessions: number;
  totalStudents: number;
  averageAttendanceRate: number;
  dataPoints: {
    sessionNumber: number;
    date: string;
    present: number;
    absent: number;
    late: number;
  }[];
}
