# ==============================================================================
# MULTI-STAGE DOCKERFILE FOR AI FACE ATTENDANCE BACKEND
# ==============================================================================
# Stage 1: Build stage (with compilers for python package wheels)
# Stage 2: Runtime stage (clean, without compilers for minimum image size)
# ==============================================================================

# ==============================================================================
# STAGE 1: Builder
# ==============================================================================
FROM python:3.11-slim-bookworm AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system-level dependencies required ONLY for building/compiling:
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up a python virtual environment to package dependencies cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install dependencies into the virtual environment
RUN pip install --upgrade pip && \
    pip install torch==2.1.1 torchvision==0.16.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# ==============================================================================
# STAGE 2: Runtime Runner
# ==============================================================================
FROM python:3.11-slim-bookworm AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the pre-built virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Install only RUNTIME dependencies (no compilers like gcc, g++, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libglib2.0-0 \
    libgl1 \
    ffmpeg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# Copy application source code with correct owner permissions
COPY --chown=appuser:appgroup ./app /app/app
COPY --chown=appuser:appgroup ./alembic.ini /app/alembic.ini

# Fix permissions on /app for the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port and start FastAPI application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]