import streamlit as st
import pandas as pd
from app.frontend.api_client import AttendanceAPI, ClassAPI

st.title("📝 Tạo báo cáo")
st.markdown("---")

st.subheader("Tạo báo cáo điểm danh")

col1, col2 = st.columns(2)

with col1:
    # Fetch classes from API
    classes = ClassAPI.get_all()
    class_options = ["Tất cả"] + [cls.get('name', '') for cls in classes] if classes else ["Tất cả"]
    class_id = st.selectbox("Chọn lớp", class_options)
    start_date = st.date_input("Ngày bắt đầu")

with col2:
    end_date = st.date_input("Ngày kết thúc")
    report_type = st.selectbox("Loại báo cáo", ["Tổng hợp", "Chi tiết", "Tóm tắt"])

if st.button("📊 Tạo báo cáo"):
    # Fetch attendance data from API
    attendance_data = AttendanceAPI.get_all()

    if attendance_data:
        # Filter data based on selected criteria
        filtered_data = []
        for record in attendance_data:
            record_date = pd.to_datetime(record.get('date', '')).date()
            record_class = record.get('class', '')

            # Check date range
            if start_date <= record_date <= end_date:
                # Check class filter
                if class_id == "Tất cả" or record_class == class_id:
                    filtered_data.append(record)

        if filtered_data:
            df = pd.DataFrame(filtered_data)

            # Calculate summary statistics
            total_records = len(filtered_data)
            present_count = len([r for r in filtered_data if r.get('status') == 'Có mặt'])
            absent_count = len([r for r in filtered_data if r.get('status') == 'Vắng'])
            late_count = len([r for r in filtered_data if r.get('status') == 'Muộn'])

            attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

            st.success(f"✓ Báo cáo {report_type} cho lớp {class_id} từ {start_date} đến {end_date} đã được tạo!")

            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Tổng bản ghi", total_records)
            with col2:
                st.metric("Có mặt", present_count)
            with col3:
                st.metric("Vắng", absent_count)
            with col4:
                st.metric("Muộn", late_count)

            st.metric("Tỷ lệ điểm danh", f"{attendance_rate:.1f}%")

            # Display detailed data
            st.subheader("Chi tiết báo cáo")
            st.dataframe(df, use_container_width=True)

            # Export functionality
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Tải báo cáo CSV",
                data=csv_data,
                file_name=f"baocao_{class_id}_{start_date}_to_{end_date}.csv",
                mime="text/csv",
                key="download_csv"
            )
        else:
            st.warning("Không có dữ liệu điểm danh trong khoảng thời gian đã chọn")
    else:
        st.error("❌ Không thể tải dữ liệu điểm danh từ API")

st.markdown("---")
st.info("💡 Báo cáo sẽ được gửi qua email sau khi tạo")
