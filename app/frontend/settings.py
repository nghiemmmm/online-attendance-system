import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.title("⚙️ Cài đặt")
st.markdown("---")

st.write(f"**Bạn đang đăng nhập với vai trò:** {st.session_state.role}")

# User settings
st.subheader("👤 Cài đặt tài khoản")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Tên người dùng")
    st.text_input("Email")
    st.selectbox("Vai trò", ["Admin", "Giáo viên", "Học sinh"])

with col2:
    st.text_input("Số điện thoại")
    st.date_input("Ngày sinh")
    st.selectbox("Phòng ban", ["Quản trị", "Giáo dục", "Hỗ trợ"])

if st.button("💾 Lưu thông tin"):
    st.success("✓ Lưu thông tin thành công!")

st.markdown("---")

# System settings
st.subheader("🖥️ Cài đặt hệ thống")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Thông báo**")
    st.checkbox("Bật thông báo email", value=True)
    st.checkbox("Bật thông báo SMS", value=False)
    st.checkbox("Bật thông báo trong ứng dụng", value=True)

with col2:
    st.markdown("**Bảo mật**")
    st.checkbox("Bật xác thực hai yếu tố", value=True)
    st.checkbox("Bất buộc thay đổi mật khẩu định kỳ", value=True)
    st.selectbox("Chế độ bảo mật", ["Cao", "Trung bình", "Thấp"])

st.markdown("---")

# Backup settings
st.subheader("💾 Sao lưu dữ liệu")

col1, col2 = st.columns(2)

with col1:
    backup_frequency = st.selectbox("Tần suất sao lưu", ["Hàng ngày", "Hàng tuần", "Hàng tháng"])
    
    if st.button("🔄 Sao lưu ngay"):
        st.success("✓ Sao lưu dữ liệu thành công!")

with col2:
    st.write("**Lần sao lưu cuối cùng:** 2024-03-08 10:30")
    st.write("**Kích thước:** 524 MB")
    
    if st.button("📥 Tải xuống sao lưu"):
        st.info("Đang chuẩn bị tệp sao lưu...")

st.markdown("---")

# Advanced settings
st.subheader("🔧 Cài đặt nâng cao")

col1, col2 = st.columns(2)

with col1:
    st.text_input("API URL", value=os.getenv("API_URL", "http://localhost:8000"))
    st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English", "中文"])

with col2:
    st.selectbox("Múi giờ", ["UTC+7", "UTC+8", "UTC+9"])
    st.selectbox("Định dạng ngày", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])

if st.button("💾 Lưu cài đặt nâng cao"):
    st.success("✓ Lưu cài đặt nâng cao thành công!")

st.markdown("---")

# Danger zone
st.subheader("⚠️ Vùng nguy hiểm")

if st.button("🔑 Đổi mật khẩu"):
    with st.form("change_password_form"):
        old_password = st.password_input("Mật khẩu cũ")
        new_password = st.password_input("Mật khẩu mới")
        confirm_password = st.password_input("Xác nhận mật khẩu")
        
        if st.form_submit_button("✓ Đổi mật khẩu"):
            if new_password == confirm_password:
                st.success("✓ Đổi mật khẩu thành công!")
            else:
                st.error("❌ Mật khẩu mới không khớp")

if st.button("🗑️ Xóa tài khoản", key="delete_account"):
    st.error("❌ Xóa tài khoản sẽ xóa tất cả dữ liệu của bạn. Không thể hoàn tác!")
    
    if st.button("✓ Xác nhận xóa"):
        st.error("✓ Tài khoản đã bị xóa")

st.info("💡 Vui lòng cẩn thận khi sử dụng các tùy chọn trong vùng nguy hiểm")