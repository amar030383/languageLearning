# German Vocabulary Learning Application

A web application for learning German vocabulary with audio support, built using FastAPI and React.

## Features

- Interactive vocabulary learning interface
- Audio playback for German words
- Word exclusion functionality
- Auto-play mode for continuous learning

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React + Vite + TypeScript
- **Containerization**: Docker
- **Proxy**: Nginx

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

## Quick Start with Docker

```bash
# Pull and run the application
docker compose pull
docker compose up -d

# Access the application
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

## Local Development Setup

### Backend
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── main.py            # Main application
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/              # Source code
│   └── package.json      # Node.js dependencies
├── german_audio/         # Audio files
├── SingeSheet.csv       # Vocabulary data
└── docker-compose.yml   # Docker configuration
```

## Docker Images

- Backend: `amar3383/german-backend:latest`
- Frontend: `amar3383/german-frontend:latest`

## Environment Variables

### Backend
- `PYTHONUNBUFFERED=1`: Unbuffered Python output

### Frontend
- `VITE_API_URL`: Backend API URL (default: http://backend:8000)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
