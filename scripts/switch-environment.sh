#!/bin/bash

# ==============================================================================
# BASH SCRIPT: DOCKER COMPOSE ENVIRONMENT SWITCHER
# Target OS: Ubuntu / Debian / Linux
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# --- COLOR DEFINITIONS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# File paths
OVERRIDE_FILE="docker-compose.override.yml"
BACKUP_FILE="docker-compose.override.yml.bak"
MAIN_COMPOSE_FILE="docker-compose.yml"

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

# --- SYSTEM CHECKS ---
check_system() {
    # Check for docker compose
    if ! docker compose version &>/dev/null; then
        log_error "Docker Compose (V2) chưa được cài đặt! Vui lòng cài đặt trước."
        exit 1
    fi

    # Check for docker daemon
    if ! docker info &>/dev/null; then
        log_error "Docker daemon chưa chạy hoặc user không có quyền chạy Docker không cần sudo!"
        exit 1
    fi

    # Check main docker-compose.yml exists
    if [ ! -f "$MAIN_COMPOSE_FILE" ]; then
        log_error "Không tìm thấy tệp tin gốc ${MAIN_COMPOSE_FILE} trong thư mục hiện tại!"
        exit 1
    fi
}

# --- BACKUP EXISTING OVERRIDE FILE ---
backup_override() {
    if [ -f "$OVERRIDE_FILE" ]; then
        log_info "Tìm thấy ${OVERRIDE_FILE} cũ. Tiến hành tạo tệp sao lưu tại ${BACKUP_FILE}..."
        cp "$OVERRIDE_FILE" "$BACKUP_FILE"
        log_success "Đã tạo sao lưu thành công."
    fi
}

# --- LOG INTERACTIVE MENUS ---
show_help() {
    echo -e "Hệ thống Điểm danh Sinh viên bằng Nhận diện Khuôn mặt AI - Bộ Chuyển Đổi Môi Trường"
    echo -e "\nCách sử dụng:"
    echo -e "  ./switch-environment.sh [dev|prod|status]"
    echo -e "\nCác tham số:"
    echo -e "  ${BLUE}dev${NC}     : Chuyển dự án sang chế độ Phát triển (Development Mode)"
    echo -e "  ${BLUE}prod${NC}    : Chuyển dự án sang chế độ Sản xuất (Production Mode)"
    echo -e "  ${BLUE}status${NC}  : Hiển thị trạng thái cấu hình môi trường hiện tại của Docker"
    echo -e ""
    exit 0
}

# ==========================================
# 1. DEVELOPMENT MODE CONFIGURATION GENERATOR
# ==========================================
enable_dev() {
    check_system
    backup_override
    
    log_info "Đang thiết lập cấu hình Development Mode..."
    if [ ! -f "docker-compose.dev.yml" ]; then
        log_error "Không tìm thấy tệp docker-compose.dev.yml để sao chép!"
        exit 1
    fi
    cp "docker-compose.dev.yml" "$OVERRIDE_FILE"
    
    log_success "Development mode enabled (✓)"
    echo -e "\nHướng dẫn vận hành tiếp theo:"
    echo -e "  1. Chạy lệnh: ${BLUE}docker compose up -d${NC} để khởi chạy chế độ dev."
    echo -e "  2. Mã nguồn được gắn (mount) trực tiếp từ máy vào container, thay đổi code sẽ tự động reload."
}

# ==========================================
# 2. PRODUCTION MODE CONFIGURATION GENERATOR
# ==========================================
enable_prod() {
    check_system
    backup_override
    
    log_info "Đang thiết lập cấu hình Production Mode..."
    if [ ! -f "docker-compose.pro.yml" ]; then
        log_error "Không tìm thấy tệp docker-compose.pro.yml để sao chép!"
        exit 1
    fi
    cp "docker-compose.pro.yml" "$OVERRIDE_FILE"
    
    log_success "Production mode enabled (✓)"
    echo -e "\n${YELLOW}⚠️ NHẮC NHỞ QUAN TRỌNG CHO PRODUCTION:${NC}"
    echo -e "  Vui lòng kiểm tra lại cấu hình các khóa nhạy cảm trong hệ thống trước khi khởi chạy:"
    echo -e "  - Tệp cấu hình môi trường (.env / .env.production)"
    echo -e "  - GitHub Secrets (cho CI/CD Pipeline)"
    echo -e "  - Biến kết nối DATABASE_URL"
    echo -e "  - Khóa bảo mật JWT_SECRET"
    echo -e "  - Đường dẫn cache REDIS_URL"
    echo -e "  - Các thông số Cloudinary & Google OAuth Integration"
}

# ==========================================
# 3. GET CURRENT CONFIGURATION STATUS
# ==========================================
show_status() {
    echo -e "====================================================="
    echo -e "🔍 ${BLUE}Current Environment Status:${NC}"
    echo -e "====================================================="
    
    if [ ! -f "$OVERRIDE_FILE" ]; then
        echo -e "Trạng thái: ${YELLOW}Không hoạt động (Chưa cấu hình tệp override)${NC}"
        echo -e "Mặc định hệ thống Docker Compose sẽ chạy tệp gốc."
        exit 0
    fi
    
    # Parse existing override configuration to check the environment mode
    if grep -q "DEBUG=true" "$OVERRIDE_FILE"; then
        echo -e "Môi trường: ${GREEN}Development Mode${NC}"
        echo -e "Backend   : ${GREEN}DEBUG=true, Port 8000 Exposed${NC}"
        echo -e "Frontend  : ${GREEN}Development Mode, Port 3000 Exposed${NC}"
        echo -e "Database  : ${GREEN}PostgreSQL (Port 5432 Exposed)${NC}"
        echo -e "Redis     : ${GREEN}Enabled (Port 6379 Exposed)${NC}"
        echo -e "AI Engine : ${GREEN}Development (Port 9000 Exposed, Local Mount)${NC}"
    else
        echo -e "Môi trường: ${BLUE}Production Mode${NC}"
        echo -e "Backend   : ${BLUE}DEBUG=false, LOG_LEVEL=warning${NC}"
        echo -e "Frontend  : ${BLUE}Production Mode, Auto-Restart Always${NC}"
        echo -e "Database  : ${BLUE}PostgreSQL (Bảo mật - Không mở cổng ra ngoài)${NC}"
        echo -e "Redis     : ${BLUE}Enabled (Bảo mật - Không mở cổng ra ngoài)${NC}"
        echo -e "AI Engine : ${BLUE}Production Mode, Auto-Restart Always${NC}"
    fi
    echo -e "====================================================="
}

# --- ARGUMENT ROUTER ---
case "$1" in
    dev)
        enable_dev
        ;;
    prod)
        enable_prod
        ;;
    status)
        show_status
        ;;
    *)
        show_help
        ;;
esac
exit 0
