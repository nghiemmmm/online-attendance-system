# Inherit from the base dependency image built in Dockerfile.deps
ARG DEPS_IMAGE=attendance-deps:latest
FROM ${DEPS_IMAGE}

WORKDIR /app

# Copy the backend source code
COPY ./app /app/app
COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

# Expose port and start FastAPI application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]