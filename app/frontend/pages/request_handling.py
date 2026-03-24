import streamlit as st
import pandas as pd
from app.frontend.api_client import RequestAPI

st.title("💬 Xử lý yêu cầu")
st.markdown("---")

st.subheader("Danh sách yêu cầu cần xử lý")

# Fetch requests from API
requests_data = RequestAPI.get_all()

if requests_data and len(requests_data) > 0:
    # Convert to DataFrame for display
    df = pd.DataFrame(requests_data)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    st.subheader("Xử lý yêu cầu")

    # Get pending requests
    pending_requests = [req for req in requests_data if req.get('status') == 'Chờ xử lý']

    if pending_requests:
        request_options = [f"{req.get('id', '')} - {req.get('type', '')}" for req in pending_requests]
        selected_request = st.selectbox("Chọn yêu cầu", request_options)

        if selected_request:
            request_id = selected_request.split(" - ")[0]
            request_data = next((req for req in pending_requests if str(req.get('id', '')) == request_id), None)

            if request_data:
                st.write(f"**Yêu cầu:** {selected_request}")
                st.write(f"**Người gửi:** {request_data.get('sender', 'N/A')}")
                st.write(f"**Ngày tạo:** {request_data.get('created_date', 'N/A')}")
                st.write(f"**Mô tả:** {request_data.get('description', 'N/A')}")

                response_text = st.text_area("Phản hồi")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Chấp nhận"):
                        update_data = {
                            "status": "Hoàn thành",
                            "response": response_text,
                            "processed_by": st.session_state.get('user_id', 'Admin')
                        }
                        result = RequestAPI.update(int(request_id), update_data)
                        if result:
                            st.success(f"✓ Đã chấp nhận {selected_request}")
                            st.rerun()
                        else:
                            st.error("❌ Lỗi khi cập nhật yêu cầu")

                with col2:
                    if st.button("❌ Từ chối"):
                        update_data = {
                            "status": "Từ chối",
                            "response": response_text,
                            "processed_by": st.session_state.get('user_id', 'Admin')
                        }
                        result = RequestAPI.update(int(request_id), update_data)
                        if result:
                            st.error(f"✗ Đã từ chối {selected_request}")
                            st.rerun()
                        else:
                            st.error("❌ Lỗi khi cập nhật yêu cầu")
    else:
        st.info("Không có yêu cầu nào đang chờ xử lý")
else:
    st.info("Không có dữ liệu yêu cầu. Vui lòng kiểm tra API.")

st.info("💡 Người gửi sẽ nhận được thông báo qua email")
