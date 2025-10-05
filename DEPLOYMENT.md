# Deployment Guide

This document explains how to run the German Vocabulary Player with Docker locally, push images to Docker Hub, and deploy a single-container app to Hugging Face Spaces.

## Prerequisites
- Docker and Docker Compose
- Docker Hub account (`docker login`)
- Hugging Face account and a Personal Access Token (HF token)

## 1) Run locally with Docker Compose

```bash
# From repo root
docker compose down -v
docker compose up -d --build

# Open
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

Sanity checks:
```bash
curl -i http://localhost:3000/api/vocabulary
curl -i http://localhost:3000/api/excluded-words
curl -X POST http://localhost:3000/api/excluded-words \
  -H "Content-Type: application/json" \
  -d '{"word_index":0}'
```

If port 8000 is in use:
- Free the port (kill process or stop container), or
- Change `backend` port mapping in `docker-compose.yml` to `"8001:8000"`, then rebuild.

## 2) Build and push to Docker Hub

Backend:
```bash
docker login -u <your_dockerhub_username>
docker build -t <your_dockerhub_username>/german-vocab-backend:latest -f backend/Dockerfile .
docker push <your_dockerhub_username>/german-vocab-backend:latest
```

Frontend:
```bash
docker build -t <your_dockerhub_username>/german-vocab-frontend:latest -f frontend/Dockerfile ./frontend
docker push <your_dockerhub_username>/german-vocab-frontend:latest
```

## 3) Deploy to Hugging Face (Docker Space)

This repository includes a single-container setup in `huggingface/`:
- `huggingface/Dockerfile.hf` runs the FastAPI backend (8000) and Nginx (7860) in one container.
- `huggingface/nginx.conf` proxies `/api` → `127.0.0.1:8000` and serves the built frontend on 7860.
- `huggingface/start.sh` starts both services.

### 3.1 Install and login to HF CLI
```bash
pip install -U huggingface_hub
huggingface-cli login
```

### 3.2 Create a Space
Via Web UI:
- Go to https://huggingface.co/spaces → Create Space
- SDK: Docker
- Hardware: CPU Basic
- Name: e.g., `german-vocabulary-player`

Via CLI:
```bash
huggingface-cli repo create <your-namespace>/german-vocabulary-player --type space --sdk docker
```

### 3.3 Connect repo to the Space and push
Add remote and push current project:
```bash
# From repo root
git remote add hf https://huggingface.co/spaces/<your-namespace>/german-vocabulary-player

git add .
git commit -m "Add Hugging Face Docker Space"
git push hf HEAD:main
```

In the Space → Settings → CI/CD:
- Set “Dockerfile path” to: `huggingface/Dockerfile.hf`

The build starts automatically. Once Running:
- Open the Space URL (port 7860 by default).
- App calls the API via `/api` and should work out-of-the-box.

### 3.4 Optional: Test HF container locally
```bash
docker build -t hf-german-vocab -f huggingface/Dockerfile.hf .
docker run --rm -p 7860:7860 hf-german-vocab
# Open http://localhost:7860
# API check:
curl -i http://localhost:7860/api/vocabulary
```

## Notes
- Frontend API calls use relative paths (e.g., `/api/...`). This works locally (via Nginx proxy in the frontend container) and on HF (via Nginx proxy in the HF container).
- If audio HEAD requests 404, it means the mp3 for that index is missing. The UI will continue without crashing.
- For security and smaller images, you can pin base images, e.g., `python:3.11-slim-bookworm`, `node:18.20-alpine`, `nginx:1.27-alpine`.

## Troubleshooting
- Space build fails: ensure the Space repo contains `backend/`, `frontend/`, and `huggingface/` directories with all required files.
- API 404 on Space: verify `huggingface/nginx.conf` has the `/api` proxy block pointing to `127.0.0.1:8000`.
- Long build times on Space: re-run build or optimize Dockerfile layers.
