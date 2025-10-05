# German Vocabulary Audio Player - Web Application

A full-stack web application for learning German vocabulary with audio playback. Built with FastAPI backend and React frontend.

## Features

- 🎵 Play German and English words with audio
- 📝 Display German and English sentences
- ⏭️ Navigate through vocabulary entries
- 🎨 Beautiful, modern UI with gradient design
- 🔊 Sequential audio playback (German word → English word → English sentence → German sentence)

## Project Structure

```
GermanFastAPI/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styling
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── german_audio/           # Audio files directory
├── SingeSheet.csv          # Vocabulary data
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd GermanFastAPI/backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
cd GermanFastAPI/frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Make sure both backend and frontend servers are running
2. Open your browser and navigate to `http://localhost:3000`
3. Click the "Play" button to hear the vocabulary in sequence
4. Use "Previous" and "Next" buttons to navigate between words
5. The currently playing text will be highlighted

## API Endpoints

### Backend API

- `GET /` - Root endpoint
- `GET /api/vocabulary` - Get all vocabulary entries
- `GET /api/vocabulary/{index}` - Get specific vocabulary entry
- `GET /api/audio/{index}/{audio_type}` - Get audio file
  - Audio types: `german_word`, `english_word`, `german_sentence`, `english_sentence`

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **Pandas** - Data manipulation and CSV reading
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS3** - Modern styling with gradients and animations

## Development

### Backend Development
The FastAPI backend provides automatic API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Development
The React frontend uses Vite for hot module replacement (HMR), so changes will reflect immediately.

## Building for Production

### Backend
The backend can be deployed using any ASGI server like Uvicorn or Gunicorn.

### Frontend
```bash
cd frontend
npm run build
```

The production build will be in the `frontend/dist` directory.

## Notes

- Audio files must be present in the `german_audio` directory
- The CSV file (`SingeSheet.csv`) must be in the root of the GermanFastAPI directory
- CORS is configured to allow requests from `localhost:3000` and `localhost:5173`

## License

This project is for educational purposes.
