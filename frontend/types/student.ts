export interface StudentProfile {
  id: string;
  name: string;
  studentId: string;
  email: string;
  phone: string;
  department: string;
  faceRegistered: boolean;
  avatarUrl?: string;
  registeredFacesCount: number;
}

export interface StudentClaim {
  id: string;
  subjectCode: string;
  subjectName: string;
  date: string;
  sessionNumber: number;
  currentStatus: 'absent' | 'late';
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  submittedAt: string;
}
