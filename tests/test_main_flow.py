import httpx
import pytest

BASE_URL = "http://127.0.0.1:5050/api/v1"

def test_main_attendance_flow():
    """
    Test kịch bản:
    1. Đăng nhập để lấy token của Admin/Giảng viên.
    2. Mở phiên điểm danh.
    3. Điểm danh tự động theo lô.
    4. Đóng phiên điểm danh.
    """
    # Do server chưa chắc đã chạy lúc pytest run, script này mang tính chất Integration/E2E test
    # Nên cần chạy server uvicorn ở một terminal khác trước khi test.

    try:
        with httpx.Client(base_url=BASE_URL) as client:
            # 1. Đăng nhập (Giả sử có tài khoản gv001/password)
            login_data = {
                "username": "gv001",
                "password": "password"
            }
            resp = client.post("/auth/access-tokens", data=login_data)
    except httpx.ConnectError:
        pytest.skip("Uvicorn server is not running, skipping E2E main attendance flow test.")

    with httpx.Client(base_url=BASE_URL) as client:
        resp = client.post("/auth/access-tokens", data=login_data)

        if resp.status_code != 200:
            pytest.skip("Không thể đăng nhập, hãy đảm bảo CSDL có tài khoản gv001 và mật khẩu 'password'")

        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Mở điểm danh cho buổi học (Giả sử có buổi học id 1)
        resp_mo = client.patch("/class-sessions/1", json={"status": "DANG_DIEN_RA"}, headers=headers)
        if resp_mo.status_code == 404:
            pytest.skip("Không tìm thấy buổi học ID 1, bỏ qua test điểm danh")

        assert resp_mo.status_code == 200, "Mở điểm danh thất bại"
        assert resp_mo.json()["status"] == "DANG_DIEN_RA"

        # 3. Điểm danh tự động (Giả sử có sinh viên id 1)
        attendance_data = {
            "class_session_id": 1,
            "student_ids": [1],
            "average_confidence": 0.9
        }
        resp_dd = client.post("/attendance-records/", json=attendance_data, headers=headers)
        assert resp_dd.status_code == 200, "Điểm danh tự động thất bại"
        assert resp_dd.json()["success"] is True

        # 4. Đóng điểm danh
        resp_dong = client.patch("/class-sessions/1", json={"status": "DA_KET_THUC"}, headers=headers)
        assert resp_dong.status_code == 200, "Đóng điểm danh thất bại"
        assert resp_dong.json()["status"] == "DA_KET_THUC"

        print("Luồng điểm danh hoạt động hoàn hảo!")

if __name__ == "__main__":
    test_main_attendance_flow()
