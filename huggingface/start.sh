#!/usr/bin/env bash
set -euo pipefail

# Start backend (FastAPI) on 8000
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start nginx serving frontend on 7860
nginx -g 'daemon off;'
