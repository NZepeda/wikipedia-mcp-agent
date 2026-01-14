FROM python:3.12-slim

WORKDIR /app

## Ensure build tools are available
## rm -rf /var/lib/apt/lists/* removes cached package lists to reduce image size
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire project
COPY mcp_server.py /app/
COPY shared/ /app/shared/
COPY backend/ /app/backend/
COPY suggested_titles.txt /app/

# Expose port (Railway will set the PORT env variable)
EXPOSE 8000

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Run the FastAPI application
CMD ["sh", "-c", "uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
