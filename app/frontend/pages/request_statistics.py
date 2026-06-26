import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.frontend.api_client import RequestAPI

st.title("📊 Thống kê yêu cầu")
st.markdown("---")

st.subheader("Thống kê yêu cầu")

# Fetch request statistics from API
stats_data = RequestAPI.get_stats()
requests_data = RequestAPI.get_all()

# Default values if API fails
total_requests = 0
pending_requests = 0
processing_requests = 0
completed_requests = 0

if stats_data:
    total_requests = stats_data.get('total', 0)
    pending_requests = stats_data.get('pending', 0)
    processing_requests = stats_data.get('processing', 0)
    completed_requests = stats_data.get('completed', 0)
elif requests_data:
    # Calculate from request list if stats API not available
    total_requests = len(requests_data)
    pending_requests = len([req for req in requests_data if req.get('status') == 'Chờ xử lý'])
    processing_requests = len([req for req in requests_data if req.get('status') == 'Đang xử lý'])
    completed_requests = len([req for req in requests_data if req.get('status') == 'Hoàn thành'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📥 Tổng yêu cầu", total_requests, "+5")

with col2:
    st.metric("⏳ Chờ xử lý", pending_requests, "-2")

with col3:
    st.metric("⚙️ Đang xử lý", processing_requests, "+1")

with col4:
    st.metric("✅ Hoàn thành", completed_requests, "+8")

st.markdown("---")

st.subheader("Chi tiết yêu cầu")

if requests_data and len(requests_data) > 0:
    df = pd.DataFrame(requests_data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Không có dữ liệu yêu cầu")

st.markdown("---")

# Statistics chart
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Biểu đồ trạng thái")

    status_counts = {
        "Hoàn thành": completed_requests,
        "Đang xử lý": processing_requests,
        "Chờ xử lý": pending_requests
    }

    fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Biểu đồ loại yêu cầu")

    if requests_data:
        # Count requests by type
        type_counts = {}
        for req in requests_data:
            req_type = req.get('type', 'Khác')
            type_counts[req_type] = type_counts.get(req_type, 0) + 1

        fig = px.bar(x=list(type_counts.keys()), y=list(type_counts.values()))
        fig.update_layout(xaxis_title="Loại", yaxis_title="Số lượng")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu để tạo biểu đồ")

st.markdown("---")

# Processing time analysis
st.subheader("⏱️ Phân tích thời gian xử lý")

if requests_data:
    # Calculate processing times for completed requests
    completed_reqs = [req for req in requests_data if req.get('status') == 'Hoàn thành']

    if completed_reqs:
        processing_times = []
        for req in completed_reqs:
            created_date = pd.to_datetime(req.get('created_date', ''))
            completed_date = pd.to_datetime(req.get('completed_date', ''))
            if pd.notna(created_date) and pd.notna(completed_date):
                processing_time = (completed_date - created_date).total_seconds() / 3600  # hours
                processing_times.append(processing_time)

        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            st.metric("Thời gian xử lý trung bình", f"{avg_time:.1f} giờ")

            # Distribution chart
            fig = px.histogram(x=processing_times, nbins=10, title="Phân bố thời gian xử lý")
            fig.update_layout(xaxis_title="Thời gian (giờ)", yaxis_title="Số yêu cầu")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có dữ liệu thời gian xử lý")
    else:
        st.info("Chưa có yêu cầu nào hoàn thành")
else:
    st.info("Không có dữ liệu để phân tích")
