# Backend Dockerfile
FROM python:3.11-slim AS backend

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Expose backend port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# # Backend Dockerfile
# FROM python:3.11-slim AS backend

# # Prevent Python from writing .pyc files and buffering stdout/stderr
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# WORKDIR /app/backend

# # System deps
# RUN apt-get update -y && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# # Copy requirements and install
# COPY backend/requirements.txt /app/backend/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend source
# COPY backend/ /app/backend/

# # Expose backend port
# EXPOSE 8000

# # Run FastAPI with Uvicorn
# CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
