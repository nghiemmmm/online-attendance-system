export interface CourseClass {
  id: number;
  maLop: string; // e.g. CS101_HK1
  tenHocPhan: string; // e.g. Lập trình cơ bản
  giangVien: string;
  hocKy: string; // e.g. HK1-2024
  siSo: number;
  siSoHienTai: number;
  trangThai: "Đang học" | "Đã kết thúc" | "Sắp mở";
}
