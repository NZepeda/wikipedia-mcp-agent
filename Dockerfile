# ============================================
# Stage 1: Builder - Install dependencies with build tools
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools (gcc) needed for compiling.
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual environment for easy copying
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ============================================
# Stage 2: Production image without build tools
# ============================================
FROM python:3.12-slim AS final

WORKDIR /app

# Copy the virtual environment from the builder stage (contains all installed packages)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY mcp_server.py /app/
COPY shared/ /app/shared/
COPY backend/ /app/backend/
COPY suggested_titles.txt /app/

# Create a non-root user for security
# Concretely, this means the application will not run with root privileges, so any potential security vulnerabilities in the application will have limited access to the host system.
RUN useradd --create-home --shell /bin/bash appuser

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Railway will set the PORT env variable)
EXPOSE 8000

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Run the FastAPI application
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
