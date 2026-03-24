import streamlit as st
import pandas as pd
from app.frontend.api_client import AttendanceAPI

st.title("📋 Điểm danh")
st.markdown("---")

st.subheader("Ghi nhận điểm danh")

col1, col2 = st.columns(2)

with col1:
    student_id = st.text_input("Mã học sinh")
    date = st.date_input("Ngày")

with col2:
    time = st.time_input("Giờ")
    status = st.selectbox("Trạng thái", ["Có mặt", "Vắng", "Muộn"])

if st.button("✅ Ghi nhận"):
    if student_id:
        data = {
            "student_id": student_id,
            "date": date.isoformat(),
            "time": time.isoformat(),
            "status": status
        }
        result = AttendanceAPI.create(data)
        if result:
            st.success(f"✓ Ghi nhận điểm danh cho học sinh {student_id} thành công!")
        else:
            st.error("❌ Lỗi khi ghi nhận. Vui lòng kiểm tra API.")
    else:
        st.error("Vui lòng nhập mã học sinh")

st.markdown("---")

st.subheader("Lịch sử điểm danh")

attendance_records = AttendanceAPI.get_all()
if attendance_records and len(attendance_records) > 0:
    df = pd.DataFrame(attendance_records)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Không có bản ghi điểm danh")
