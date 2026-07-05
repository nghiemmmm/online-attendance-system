import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")


class APIClient:
    """Client để gọi FastAPI endpoints"""

    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, endpoint: str, **kwargs) -> dict[str, Any] | None:
        """GET request"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error GET {endpoint}: {e}")
            return None

    def post(
        self, endpoint: str, data: dict = None, json: dict = None, **kwargs
    ) -> dict[str, Any] | None:
        """POST request"""
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}", data=data, json=json, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error POST {endpoint}: {e}")
            return None

    def put(self, endpoint: str, json: dict = None, **kwargs) -> dict[str, Any] | None:
        """PUT request"""
        try:
            response = self.session.put(
                f"{self.base_url}{endpoint}", json=json, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error PUT {endpoint}: {e}")
            return None

    def delete(self, endpoint: str, **kwargs) -> dict[str, Any] | None:
        """DELETE request"""
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json() if response.text else {"status": "success"}
        except requests.exceptions.RequestException as e:
            print(f"Error DELETE {endpoint}: {e}")
            return None

    def close(self):
        """Đóng session"""
        self.session.close()


# Singleton client instance
api_client = APIClient()


# API Endpoints
class StudentAPI:
    """API endpoints cho học sinh"""

    @staticmethod
    def get_all() -> list | None:
        """Lấy danh sách tất cả học sinh"""
        response = api_client.get("/api/students")
        return response if isinstance(response, list) else []

    @staticmethod
    def create(data: dict) -> dict | None:
        """Tạo học sinh mới"""
        return api_client.post("/api/students", json=data)

    @staticmethod
    def update(student_id: int, data: dict) -> dict | None:
        """Cập nhật thông tin học sinh"""
        return api_client.put(f"/api/students/{student_id}", json=data)

    @staticmethod
    def delete(student_id: int) -> dict | None:
        """Xóa học sinh"""
        return api_client.delete(f"/api/students/{student_id}")

    @staticmethod
    def get_by_id(student_id: int) -> dict | None:
        """Lấy thông tin học sinh"""
        return api_client.get(f"/api/students/{student_id}")


class TeacherAPI:
    """API endpoints cho giáo viên"""

    @staticmethod
    def get_all() -> list | None:
        """Lấy danh sách tất cả giáo viên"""
        response = api_client.get("/api/teachers")
        return response if isinstance(response, list) else []

    @staticmethod
    def create(data: dict) -> dict | None:
        """Tạo giáo viên mới"""
        return api_client.post("/api/teachers", json=data)

    @staticmethod
    def update(teacher_id: int, data: dict) -> dict | None:
        """Cập nhật thông tin giáo viên"""
        return api_client.put(f"/api/teachers/{teacher_id}", json=data)

    @staticmethod
    def delete(teacher_id: int) -> dict | None:
        """Xóa giáo viên"""
        return api_client.delete(f"/api/teachers/{teacher_id}")

    @staticmethod
    def get_by_id(teacher_id: int) -> dict | None:
        """Lấy thông tin giáo viên"""
        return api_client.get(f"/api/teachers/{teacher_id}")


class AttendanceAPI:
    """API endpoints cho điểm danh"""

    @staticmethod
    def get_all() -> list | None:
        """Lấy danh sách điểm danh"""
        response = api_client.get("/api/attendance")
        return response if isinstance(response, list) else []

    @staticmethod
    def create(data: dict) -> dict | None:
        """Tạo bản ghi điểm danh"""
        return api_client.post("/api/attendance", json=data)

    @staticmethod
    def get_stats(days: int = 7) -> dict | None:
        """Lấy thống kê điểm danh"""
        return api_client.get(f"/api/attendance/stats?days={days}")


class RequestAPI:
    """API endpoints cho quản lý yêu cầu"""

    @staticmethod
    def get_all() -> list | None:
        """Lấy danh sách tất cả yêu cầu"""
        response = api_client.get("/api/requests")
        return response if isinstance(response, list) else []

    @staticmethod
    def create(data: dict) -> dict | None:
        """Tạo yêu cầu mới"""
        return api_client.post("/api/requests", json=data)

    @staticmethod
    def update(request_id: int, data: dict) -> dict | None:
        """Cập nhật trạng thái yêu cầu"""
        return api_client.put(f"/api/requests/{request_id}", json=data)

    @staticmethod
    def get_stats() -> dict | None:
        """Lấy thống kê yêu cầu"""
        return api_client.get("/api/requests/stats")
