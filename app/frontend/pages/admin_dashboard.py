import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from app.frontend.api_client import StudentAPI, TeacherAPI, AttendanceAPI, ClassAPI

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("🖥️ Bảng điều khiển Admin")
st.markdown("---")

# Fetch real data from API
students = StudentAPI.get_all()
teachers = TeacherAPI.get_all()
classes = ClassAPI.get_all()
attendance_stats = AttendanceAPI.get_stats(days=7)

# Calculate metrics
total_students = len(students) if students else 0
total_teachers = len(teachers) if teachers else 0
total_classes = len(classes) if classes else 0

# Mock attendance rate for today (replace with real API call)
today_attendance = "89%"  # This should come from API

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👤 Tổng học sinh", total_students, "+5 tuần này")

with col2:
    st.metric("👨‍🏫 Tổng giáo viên", total_teachers, "+1 tuần này")

with col3:
    st.metric("📍 Tổng lớp", total_classes, "0 tuần này")

with col4:
    st.metric("✅ Điểm danh hôm nay", today_attendance, "+2% so hôm qua")

st.markdown("---")

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Thống kê điểm danh 7 ngày qua")

    if attendance_stats and 'attendance_rates' in attendance_stats:
        days = attendance_stats.get('days', ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'])
        attendance = attendance_stats.get('attendance_rates', [85, 87, 86, 88, 90, 89, 85])

        fig = go.Figure(data=[
            go.Bar(x=days, y=attendance, marker_color='lightblue')
        ])
        fig.update_layout(height=300, xaxis_title="Ngày", yaxis_title="Tỷ lệ (%)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu thống kê điểm danh")

with col2:
    st.subheader("🏫 Phân bố học sinh theo lớp")

    if classes:
        # Count students per class
        class_counts = {}
        for cls in classes:
            class_name = cls.get('name', 'Unknown')
            class_counts[class_name] = 0

        if students:
            for student in students:
                student_class = student.get('class', 'Unknown')
                if student_class in class_counts:
                    class_counts[student_class] += 1

        classes_list = list(class_counts.keys())
        students_count = list(class_counts.values())

        fig = px.pie(values=students_count, names=classes_list, hole=0.3)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu lớp học")

st.markdown("---")

# Recent activity
st.subheader("🔔 Hoạt động gần đây")

# Mock activity data - replace with real API call
activity_data = {
    "Thời gian": ["10:30", "09:45", "09:15", "08:50", "08:20"],
    "Sự kiện": [
        "Điểm danh hoàn thành lớp 10A",
        "Thêm học sinh Trần Hương Nhi vào lớp 11B",
        "Thay đổi giáo viên lớp 10C",
        "Điểm danh hoàn thành lớp 10B",
        "Khởi động hệ thống"
    ],
    "Người dùng": ["Nguyễn Quốc Anh", "Admin", "Admin", "Trần Hương Ly", "System"]
}

df_activity = pd.DataFrame(activity_data)
st.dataframe(df_activity, use_container_width=True, hide_index=True)

st.markdown("---")

# System settings section
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ Cài đặt hệ thống")

    if st.checkbox("Bật thông báo"):
        st.caption("✓ Thông báo đã bật")

    if st.checkbox("Chế độ bảo trì"):
        st.warning("⚠️ Chế độ bảo trì đã bật")

    backup_frequency = st.selectbox("Tần suất sao lưu", ["Hàng ngày", "Hàng tuần", "Hàng tháng"])

with col2:
    st.subheader("🔐 Bảo mật")

    if st.button("Đổi mật khẩu"):
        st.info("Chức năng đổi mật khẩu sẽ được mở trong cửa sổ mới")

    if st.button("Xem nhật ký truy cập"):
        st.info("Xem nhật ký truy cập của hệ thống")

    if st.button("Sao lưu dữ liệu"):
        st.success("Sao lưu dữ liệu thành công!")

st.markdown("---")

# Footer
st.caption("🕐 Cập nhật lần cuối: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
