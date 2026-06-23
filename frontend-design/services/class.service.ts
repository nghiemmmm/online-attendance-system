import { CourseClass } from "@/types/class";
import { mockClasses } from "@/lib/mock-data/classes";

export const ClassService = {
  getClasses: async (): Promise<CourseClass[]> => {
    return new Promise((resolve, reject) => {
      // Giả lập network delay 1 giây
      setTimeout(() => {
        // Giả lập tỉ lệ 10% lỗi mạng để test trạng thái Error
        if (Math.random() < 0.1) {
          reject(new Error("Không thể kết nối với máy chủ. Vui lòng kiểm tra đường truyền và thử lại."));
        } else {
          resolve(mockClasses);
        }
      }, 1000);
    });
  }
};
