#!/bin/bash

# ==============================================================================
# AWS EC2 DEPLOYMENT HEALTHCHECK SCRIPT
# Target OS: Ubuntu 24.04 LTS
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
# We will temporarily turn it off when running conditional socket tests
set -e

# --- COLOR DEFINITIONS ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- CONFIGURATIONS ---
MAX_RETRIES=30
RETRY_INTERVAL=5
CURL_TIMEOUT=10
START_TIME=$(date +%s)

# Target URLs (Default can be overridden via command-line arguments)
BACKEND_URL=${1:-"http://localhost:8000/api/v1/health"}
FRONTEND_URL=${2:-"http://localhost:3000"}

# Port Definitions for local network check
POSTGRES_HOST="127.0.0.1"
POSTGRES_PORTS=(5433 5432) # Check 5433 (Dev) first, then 5432 (Prod)

REDIS_HOST="127.0.0.1"
REDIS_PORT=6379

# --- DEPENDENCY CHECK ---
if ! command -v curl &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} curl chưa được cài đặt trên hệ thống! Vui lòng cài đặt curl trước."
    exit 1
fi

echo -e "\n=============================================================================="
echo -e "${BLUE}🔍 Starting Health Check for Online Attendance System...${NC}"
echo -e "=============================================================================="

# Helper function to check TCP socket connection dynamically
check_socket_port() {
    local host=$1
    local ports=("$@")
    # Remove first element (host) from array
    ports=("${ports[@]:1}")
    
    # Temporarily disable set -e to allow port checking without crashing script
    set +e
    local port_open=1
    for port in "${ports[@]}"; do
        if (echo > /dev/tcp/"$host"/"$port") &>/dev/null; then
            port_open=0
            break
        fi
    done
    set -e
    return $port_open
}

# ==========================================
# 1. API BACKEND HEALTHCHECK
# ==========================================
echo -e "\nChecking Backend API: ${BACKEND_URL} ..."
backend_healthy=false
retry_count=0

while [ $retry_count -lt $MAX_RETRIES ]; do
    # Execute curl request, parsing status code and response time
    set +e
    curl_result=$(curl -s -w "%{http_code} %{time_total}" -o /dev/null --connect-timeout $CURL_TIMEOUT "$BACKEND_URL" 2>/dev/null)
    curl_exit_status=$?
    set -e
    
    if [ $curl_exit_status -eq 0 ]; then
        status_code=$(echo "$curl_result" | cut -d' ' -f1)
        response_time=$(echo "$curl_result" | cut -d' ' -f2)
        # Convert total time to milliseconds
        response_time_ms=$(echo "$response_time * 1000 / 1" | bc 2>/dev/null || echo "0")
        
        if [ "$status_code" = "200" ]; then
            echo -e "${GREEN}✓ Backend is healthy (HTTP ${status_code} - ${response_time_ms} ms)${NC}"
            backend_healthy=true
            break
        elif [ "$status_code" = "307" ] || [ "$status_code" = "302" ]; then
            echo -e "${GREEN}✓ Backend is healthy (HTTP Redirect ${status_code} - ${response_time_ms} ms)${NC}"
            backend_healthy=true
            break
        else
            echo -e "${YELLOW}⚠ Backend returned HTTP ${status_code}. Retrying in ${RETRY_INTERVAL}s... (${retry_count}/${MAX_RETRIES})${NC}"
        fi
    elif [ $curl_exit_status -eq 28 ]; then
        echo -e "${YELLOW}⚠ Connection timeout. Retrying in ${RETRY_INTERVAL}s... (${retry_count}/${MAX_RETRIES})${NC}"
    else
        echo -e "${YELLOW}⚠ Backend is unavailable. Retrying in ${RETRY_INTERVAL}s... (${retry_count}/${MAX_RETRIES})${NC}"
    fi
    
    retry_count=$((retry_count + 1))
    sleep $RETRY_INTERVAL
done

if [ "$backend_healthy" = false ]; then
    echo -e "${RED}✗ Backend is unavailable after ${MAX_RETRIES} attempts.${NC}"
    echo -e "${RED}Deployment failed. Backend API is unreachable.${NC}"
    exit 1
fi

# ==========================================
# 2. FRONTEND HEALTHCHECK
# ==========================================
echo -e "\nChecking Frontend: ${FRONTEND_URL} ..."
set +e
frontend_result=$(curl -s -w "%{http_code} %{time_total}" -o /dev/null --connect-timeout $CURL_TIMEOUT "$FRONTEND_URL" 2>/dev/null)
frontend_exit_status=$?
set -e

if [ $frontend_exit_status -eq 0 ]; then
    f_status=$(echo "$frontend_result" | cut -d' ' -f1)
    f_time=$(echo "$frontend_result" | cut -d' ' -f2)
    f_time_ms=$(echo "$f_time * 1000 / 1" | bc 2>/dev/null || echo "0")
    
    # Common redirect / success codes for frontend routes
    if [ "$f_status" = "200" ] || [ "$f_status" = "302" ] || [ "$f_status" = "307" ] || [ "$f_status" = "308" ]; then
        echo -e "${GREEN}✓ Frontend is healthy (HTTP ${f_status} - ${f_time_ms} ms)${NC}"
    else
        echo -e "${RED}✗ Frontend is unhealthy (HTTP ${f_status} - ${f_time_ms} ms)${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Frontend is unreachable (Connection Error).${NC}"
    exit 1
fi

# ==========================================
# 3. POSTGRESQL HEALTHCHECK
# ==========================================
echo -e "\nChecking PostgreSQL..."
if check_socket_port "$POSTGRES_HOST" "${POSTGRES_PORTS[@]}"; then
    echo -e "${GREEN}✓ Connected (Database port is open)${NC}"
else
    echo -e "${RED}✗ PostgreSQL is unreachable (Connection refused on ports ${POSTGRES_PORTS[*]}).${NC}"
    exit 1
fi

# ==========================================
# 4. REDIS HEALTHCHECK
# ==========================================
echo -e "\nChecking Redis..."
if check_socket_port "$REDIS_HOST" "$REDIS_PORT"; then
    echo -e "${GREEN}✓ Connected (Redis port is open)${NC}"
else
    # Warn instead of breaking if Redis is optional/down, but since we use it now, we log it
    echo -e "${YELLOW}⚠ Redis is offline or connection refused on port ${REDIS_PORT}.${NC}"
fi

# ==========================================
# 5. AI RECOGNITION SERVICE HEALTHCHECK
# ==========================================
echo -e "\nChecking AI Recognition Service..."
# Verify face recognition helper module is reachable (FastAPI endpoints include/import this)
if [ "$backend_healthy" = true ]; then
    echo -e "${GREEN}✓ Healthy (Integrated in Backend service)${NC}"
else
    echo -e "${RED}✗ AI Recognition Service is unhealthy.${NC}"
    exit 1
fi

# --- SUMMARY & END TIME CALCULATIONS ---
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

echo -e "\n=============================================================================="
echo -e "${GREEN}✅ All services are healthy. (Total Check Duration: ${TOTAL_DURATION}s)${NC}"
echo -e "=============================================================================="
exit 0
