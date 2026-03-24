import os
from turtle import home

from app.api import routes
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
import cv2
from PIL import Image
import numpy as np
import time
import base64
from io import BytesIO
import requests

from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")
if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Requester", "Responder", "Admin"]

# =========================
# LOGIN FUNCTION
# =========================
def login():
    st.header("Log in")

    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()

# =========================
# LOGOUT FUNCTION
# =========================
def logout():
    st.session_state.role = None
    st.rerun()

role = st.session_state.role

# =========================
# GLOBAL UI
# =========================
st.title("Request Manager")

# =========================
# PAGE DEFINITIONS
# =========================
st.logo("app/frontend/images/horizontal_blue.png", icon_image="app/frontend/images/icon_blue.png")
login_page = st.Page(login, title="Login", icon=":material/login:")
logout_page = st.Page(logout, title="Logout", icon=":material/logout:")
settings_page = st.Page("settings.py", title="Settings", icon=":material/settings:")

# -------- DASHBOARD & ADMIN PAGES --------
admin_dashboard = st.Page(
    "pages/admin_dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=(role == "Admin"),
)

admin_students = st.Page(
    "pages/admin_students.py",
    title="Quản lý Học sinh",
    icon=":material/groups:",
)

admin_teachers = st.Page(
    "pages/admin_teachers.py",
    title="Quản lý Giáo viên",
    icon=":material/school:",
)

admin_pages = [admin_dashboard, admin_students, admin_teachers]

# -------- REQUEST/ATTENDANCE PAGES --------
attendance_page = st.Page(
    "pages/attendance.py",
    title="Điểm danh",
    icon=":material/check_circle:",
    default=(role == "Requester"),
)

reports_page = st.Page(
    "pages/reports.py",
    title="Báo cáo",
    icon=":material/assessment:",
)

request_pages = [attendance_page, reports_page]

# -------- RESPOND PAGES --------
request_handling_page = st.Page(
    "pages/request_handling.py",
    title="Xử lý Yêu cầu",
    icon=":material/task_alt:",
    default=(role == "Responder"),
)

request_stats_page = st.Page(
    "pages/request_statistics.py",
    title="Thống kê",
    icon=":material/analytics:",
)

respond_pages = [request_handling_page, request_stats_page]

# -------- ACCOUNT PAGES --------
account_pages = [logout_page, settings_page]

# =========================
# BUILD PAGE DICTIONARY
# =========================
page_dict = {}

if role in ["Requester", "Admin"]:
    page_dict["📋 Yêu cầu"] = request_pages

if role in ["Responder", "Admin"]:
    page_dict["💬 Phản hồi"] = respond_pages

if role == "Admin":
    page_dict["⚙️ Quản lý"] = admin_pages

# =========================
# NAVIGATION
# =========================
if len(page_dict) > 0:
    pg = st.navigation({"👤 Tài khoản": account_pages} | page_dict)
else:
    pg = st.navigation([login_page])

# =========================
# RUN PAGE
# =========================
pg.run()
# }
# routes = {
#     "home": home.show,
#     # "classes": classes.show,
#     # "face_register": face_register.show,
#     # "attendance": attendance.show
# }

# page = st.query_params.get("page", "home")

# routes.get(page, home.show)()

