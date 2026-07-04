# ==============================================================================
# MULTI-STAGE DOCKERFILE FOR AI FACE ATTENDANCE BACKEND
# ==============================================================================
# Stage 1 (deps): System packages + Python dependencies (heavily cached)
# Stage 2 (app):  Application source code (changes frequently)
# ==============================================================================

# ==============================================================================
# STAGE 1: Dependencies
# ==============================================================================
FROM python:3.11-slim-bookworm AS deps

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system-level dependencies required for compilation and runtime:
# - build-essential, gcc, g++: Compile native Python extensions (faiss, insightface)
# - libpq-dev: PostgreSQL client (psycopg)
# - libglib2.0-0, libgl1: OpenCV runtime
# - ffmpeg: Media processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    libpq-dev \
    libglib2.0-0 \
    libgl1 \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser && \
    chown -R appuser:appgroup /app

# Install Python packages (cached unless requirements.txt changes)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip check

# ==============================================================================
# STAGE 2: Application
# ==============================================================================
FROM deps AS app

WORKDIR /app

# Copy backend source code
COPY ./app /app/app
COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

# Switch to non-root user
USER appuser

# Expose port and start FastAPI application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]