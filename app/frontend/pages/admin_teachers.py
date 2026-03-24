import streamlit as st
import pandas as pd
from app.frontend.api_client import TeacherAPI

st.title("👨‍🏫 Quản lý Giáo viên")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Danh sách giáo viên", "Thêm giáo viên", "Cập nhật", "Xóa"])

with tab1:
    st.subheader("Danh sách giáo viên")
    
    teachers = TeacherAPI.get_all()
    
    if teachers and len(teachers) > 0:
        df = pd.DataFrame(teachers)
        st.dataframe(df, use_container_width=True)
        
        if st.button("📥 Xuất Excel"):
            st.success("Đã xuất danh sách giáo viên")
    else:
        st.info("Không có dữ liệu giáo viên. Vui lòng thêm giáo viên mới.")

with tab2:
    st.subheader("Thêm giáo viên mới")
    
    col1, col2 = st.columns(2)
    with col1:
        teacher_id = st.text_input("Mã giáo viên")
        teacher_name = st.text_input("Tên giáo viên")
        teacher_email = st.text_input("Email")
    
    with col2:
        teacher_subject = st.selectbox("Chuyên môn", ["Toán", "Văn", "Anh", "Lý", "Hóa", "Sinh"])
        teacher_dob = st.date_input("Ngày sinh")
        teacher_phone = st.text_input("Số điện thoại")
    
    if st.button("➕ Thêm giáo viên"):
        if teacher_id and teacher_name and teacher_email:
            data = {
                "id": teacher_id,
                "name": teacher_name,
                "email": teacher_email,
                "subject": teacher_subject,
                "dob": teacher_dob.isoformat(),
                "phone": teacher_phone
            }
            result = TeacherAPI.create(data)
            if result:
                st.success(f"✓ Thêm giáo viên {teacher_name} thành công!")
            else:
                st.error("❌ Lỗi khi thêm giáo viên. Vui lòng kiểm tra API.")
        else:
            st.error("Vui lòng điền đầy đủ thông tin")

with tab3:
    st.subheader("Cập nhật thông tin giáo viên")
    
    teachers = TeacherAPI.get_all()
    if teachers:
        teacher_options = [f"{t.get('id', '')} - {t.get('name', '')}" for t in teachers]
        selected_teacher = st.selectbox("Chọn giáo viên", teacher_options)
        
        if selected_teacher:
            teacher_id = selected_teacher.split(" - ")[0]
            teacher_data = next((t for t in teachers if str(t.get('id', '')) == teacher_id), None)
            
            if teacher_data:
                col1, col2 = st.columns(2)
                with col1:
                    updated_name = st.text_input("Tên", value=teacher_data.get('name', ''))
                    updated_email = st.text_input("Email", value=teacher_data.get('email', ''))
                
                with col2:
                    updated_subject = st.selectbox("Chuyên môn", ["Toán", "Văn", "Anh"], index=0)
                    updated_status = st.selectbox("Trạng thái", ["Hoạt động", "Tạm dừng"], index=0)
                
                if st.button("💾 Cập nhật"):
                    data = {
                        "name": updated_name,
                        "email": updated_email,
                        "subject": updated_subject,
                        "status": updated_status
                    }
                    result = TeacherAPI.update(int(teacher_id), data)
                    if result:
                        st.success("✓ Cập nhật thông tin thành công!")
                    else:
                        st.error("❌ Lỗi khi cập nhật. Vui lòng kiểm tra API.")

with tab4:
    st.subheader("Xóa giáo viên")
    
    teachers = TeacherAPI.get_all()
    if teachers:
        teacher_options = [f"{t.get('id', '')} - {t.get('name', '')}" for t in teachers]
        teacher_to_delete = st.selectbox("Chọn giáo viên để xóa", teacher_options)
        
        if st.button("🗑️ Xóa", key="delete_teacher"):
            st.warning(f"⚠️ Bạn có chắc chắn muốn xóa {teacher_to_delete}?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Xác nhận xóa"):
                    teacher_id = teacher_to_delete.split(" - ")[0]
                    result = TeacherAPI.delete(int(teacher_id))
                    if result:
                        st.error(f"✓ Đã xóa {teacher_to_delete}")
                    else:
                        st.error("❌ Lỗi khi xóa. Vui lòng kiểm tra API.")
            with col2:
                if st.button("✗ Hủy"):
                    st.info("Hủy xóa")

st.markdown("---")
st.info("💡 Mẹo: Sử dụng các tab ở trên để quản lý danh sách giáo viên")
