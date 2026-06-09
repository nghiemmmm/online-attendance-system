import streamlit as st
import pandas as pd
from app.frontend.api_client import StudentAPI

st.title("👨‍🎓 Quản lý Học sinh")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Danh sách học sinh", "Thêm học sinh", "Cập nhật", "Xóa"])

with tab1:
    st.subheader("Danh sách học sinh")
    
    students = StudentAPI.get_all()
    
    if students and len(students) > 0:
        df = pd.DataFrame(students)
        st.dataframe(df, use_container_width=True)
        
        if st.button("📥 Xuất Excel"):
            st.success("Đã xuất danh sách học sinh")
    else:
        st.info("Không có dữ liệu học sinh. Vui lòng thêm học sinh mới.")

with tab2:
    st.subheader("Thêm học sinh mới")
    
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Mã học sinh")
        student_name = st.text_input("Tên học sinh")
        student_email = st.text_input("Google Email")
    
    with col2:
        student_class = st.selectbox("Lớp", ["10A", "10B", "10C", "11A", "11B"])
        student_dob = st.date_input("Ngày sinh")
        student_phone = st.text_input("Số điện thoại")
    
    if st.button("➕ Thêm học sinh"):
        if student_id and student_name and student_email:
            data = {
                "id": student_id,
                "name": student_name,
                "google_email": student_email,
                "class": student_class,
                "dob": student_dob.isoformat(),
                "phone": student_phone
            }
            result = StudentAPI.create(data)
            if result:
                st.success(f"✓ Thêm học sinh {student_name} thành công!")
            else:
                st.error("❌ Lỗi khi thêm học sinh. Vui lòng kiểm tra API.")
        else:
            st.error("Vui lòng điền đầy đủ thông tin")

with tab3:
    st.subheader("Cập nhật thông tin học sinh")
    
    students = StudentAPI.get_all()
    if students:
        student_options = [f"{s.get('id', '')} - {s.get('name', '')}" for s in students]
        selected_student = st.selectbox("Chọn học sinh", student_options)
        
        if selected_student:
            student_id = selected_student.split(" - ")[0]
            student_data = next((s for s in students if str(s.get('id', '')) == student_id), None)
            
            if student_data:
                col1, col2 = st.columns(2)
                with col1:
                    updated_name = st.text_input("Tên", value=student_data.get('name', ''))
                    updated_email = st.text_input("Google Email", value=student_data.get('google_email', ''))
                
                with col2:
                    updated_class = st.selectbox("Lớp", ["10A", "10B"], index=0)
                    updated_status = st.selectbox("Trạng thái", ["Hoạt động", "Tạm dừng"], index=0)
                
                if st.button("💾 Cập nhật"):
                    data = {
                        "name": updated_name,
                        "google_email": updated_email,
                        "class": updated_class,
                        "status": updated_status
                    }
                    result = StudentAPI.update(int(student_id), data)
                    if result:
                        st.success("✓ Cập nhật thông tin thành công!")
                    else:
                        st.error("❌ Lỗi khi cập nhật. Vui lòng kiểm tra API.")

with tab4:
    st.subheader("Xóa học sinh")
    
    students = StudentAPI.get_all()
    if students:
        student_options = [f"{s.get('id', '')} - {s.get('name', '')}" for s in students]
        student_to_delete = st.selectbox("Chọn học sinh để xóa", student_options)
        
        if st.button("🗑️ Xóa", key="delete_student"):
            st.warning(f"⚠️ Bạn có chắc chắn muốn xóa {student_to_delete}?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Xác nhận xóa"):
                    student_id = student_to_delete.split(" - ")[0]
                    result = StudentAPI.delete(int(student_id))
                    if result:
                        st.error(f"✓ Đã xóa {student_to_delete}")
                    else:
                        st.error("❌ Lỗi khi xóa. Vui lòng kiểm tra API.")
            with col2:
                if st.button("✗ Hủy"):
                    st.info("Hủy xóa")

st.markdown("---")
st.info("💡 Mẹo: Sử dụng các tab ở trên để quản lý danh sách học sinh")
