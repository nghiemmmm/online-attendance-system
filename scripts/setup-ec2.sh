#!/bin/bash

# ==============================================================================
# AWS EC2 INITIALIZATION SCRIPT FOR ONLINE ATTENDANCE SYSTEM
# Target OS: Ubuntu 24.04 LTS
# ==============================================================================

# Exit immediately if any command exits with a non-zero status
set -e

# --- COLOR DEFINITIONS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- HELPER LOGGING FUNCTIONS ---
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- STEP 1: INTERNET CONNECTION CHECK ---
log_info "Kiểm tra kết nối Internet..."
if curl -sf https://www.google.com > /dev/null; then
    log_success "Kết nối Internet: OK."
else
    log_error "Không có kết nối Internet! Vui lòng kiểm tra lại cấu hình mạng của EC2."
    exit 1
fi

# --- STEP 2: SYSTEM UPDATE & UPGRADE ---
log_info "Cập nhật danh sách gói hệ thống (Apt Update & Upgrade)..."
sudo apt-get update
sudo apt-get upgrade -y
log_success "Hệ thống đã được cập nhật."

# --- STEP 3: DOCKER & GIT INSTALLATION CHECK ---
log_info "Kiểm tra và cài đặt Git, curl, unzip..."
sudo apt-get install -y git curl unzip --no-install-recommends
log_success "Đã cài đặt các gói công cụ cơ bản."

log_info "Kiểm tra và cài đặt Docker & Docker Compose..."
# Install Docker and the Docker Compose V2 plugin from standard Ubuntu repository
if ! command -v docker &> /dev/null; then
    log_info "Docker chưa được cài đặt. Tiến hành cài đặt Docker..."
    sudo apt-get install -y docker.io docker-compose-v2 --no-install-recommends
    log_success "Docker & Docker Compose đã được cài đặt thành công."
else
    log_success "Docker đã được cài đặt từ trước."
fi

# --- STEP 4: SERVICE MANAGEMENT & USER PERMISSIONS ---
log_info "Khởi động và kích hoạt Docker Service tự động chạy cùng hệ thống..."
sudo systemctl start docker
sudo systemctl enable docker

log_info "Cấu hình quyền chạy Docker cho tài khoản người dùng hiện tại ($USER)..."
# Add current user to 'docker' group to run commands without 'sudo'
if ! groups $USER | grep -q "\bdocker\b"; then
    sudo usermod -aG docker $USER
    log_warning "Tài khoản $USER đã được thêm vào nhóm 'docker'. Lưu ý: Bạn cần SSH lại (đăng xuất rồi đăng nhập lại) để quyền này có hiệu lực."
else
    log_success "Tài khoản $USER đã có quyền chạy Docker không cần root."
fi

# Verify Docker daemon is running successfully
if sudo docker info &> /dev/null; then
    log_success "Docker daemon đang hoạt động bình thường."
else
    log_error "Docker daemon chưa chạy! Vui lòng kiểm tra lại bằng lệnh: sudo systemctl status docker"
    exit 1
fi

# --- STEP 5: REPOSITORY CLONE / UPDATE ---
PROJECT_DIR="/home/$USER/online-attendance-system"
REPO_URL="https://github.com/nghiemmmm/online-attendance-system.git"

if [ -d "$PROJECT_DIR" ]; then
    log_warning "Thư mục dự án đã tồn tại ở: $PROJECT_DIR."
    log_info "Tiến hành đồng bộ cập nhật source code mới nhất bằng Git Pull..."
    cd "$PROJECT_DIR"
    git fetch origin
    git pull
    log_success "Cập nhật mã nguồn thành công."
else
    log_info "Tiến hành tải mã nguồn từ Github về thư mục: $PROJECT_DIR..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    log_success "Tải mã nguồn dự án thành công."
fi

# --- STEP 6: ENVIRONMENT VARIABLES TEMPLATE CREATION ---
ENV_EXAMPLE_PATH="$PROJECT_DIR/.env.example"
log_info "Tạo tệp cấu hình biến môi trường mẫu .env.example..."

cat <<EOF > "$ENV_EXAMPLE_PATH"
# ==============================================================================
# ONLINE ATTENDANCE SYSTEM - ENVIRONMENT VARIABLES TEMPLATE
# ==============================================================================
# Copy this file to '.env' and fill in the values for deployment.
# DO NOT check in the actual secrets/passwords to git!

# Database connection URL (PostgreSQL)
DATABASE_URL=

# Security encryption keys
JWT_SECRET=

# Mail Configurations (SMTP)
MAIL_USERNAME=
MAIL_PASSWORD=

# Object Storage Credentials (Cloudinary)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Google OAuth Integration
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Redis Service URL
REDIS_URL=

# NextAuth Settings (Frontend Security)
NEXTAUTH_SECRET=
NEXTAUTH_URL=

# App Environment settings
NODE_ENV=production
EOF

log_success "Đã tạo thành công tệp tin mẫu cấu hình: $ENV_EXAMPLE_PATH"

# --- STEP 7: SUMMARY & NEXT STEPS ---
echo -e "\n=============================================================================="
echo -e "${GREEN}🎉 QUÁ TRÌNH KHỞI TẠO MÁY CHỦ EC2 ĐÃ HOÀN TẤT THÀNH CÔNG! 🎉${NC}"
echo -e "=============================================================================="
echo -e "1. ${BLUE}Đường dẫn thư mục dự án:${NC}"
echo -e "   cd $PROJECT_DIR"
echo -e "2. ${BLUE}Lệnh tạo và chỉnh sửa cấu hình biến môi trường (.env):${NC}"
echo -e "   cp .env.example .env && nano .env"
echo -e "3. ${BLUE}Lệnh biên dịch toàn bộ Docker container:${NC}"
echo -e "   docker compose build"
echo -e "4. ${BLUE}Lệnh chạy hệ thống ngầm trong nền:${NC}"
echo -e "   docker compose up -d"
echo -e "5. ${BLUE}Lệnh xem log giám sát hoạt động của hệ thống:${NC}"
echo -e "   docker compose logs -f"
echo -e "6. ${BLUE}Lệnh cập nhật mã nguồn mới nhất:${NC}"
echo -e "   git pull"
echo -e "7. ${BLUE}Lệnh khởi động lại toàn bộ hệ thống container:${NC}"
echo -e "   docker compose restart"
echo -e "=============================================================================="
log_warning "LƯU Ý QUAN TRỌNG: Hãy thoát phiên SSH hiện tại và kết nối lại (hoặc chạy lệnh 'newgrp docker') để quyền chạy Docker không cần sudo có hiệu lực hoàn toàn."
echo -e "=============================================================================="
