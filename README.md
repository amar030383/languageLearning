# 🇩🇪 German Language Learning Application

A modern, interactive web application for learning German vocabulary with audio playback and translation features. Built with React frontend and FastAPI backend.

## 🚀 Features

### 🎵 Vocabulary Player
- **Audio Playback**: Listen to German words and sentences with authentic pronunciation
- **AutoPlay Mode**: Continuous playback through vocabulary list
- **Speed Control**: Adjustable playback speed for German sentences (0.5x to 1.0x)
- **Visual Feedback**: Highlights currently playing text
- **Progress Tracking**: Shows current position in vocabulary list
- **Navigation**: Previous/Next buttons for manual control

### 🌐 Word Translator
- **English to German Translation**: Enter English words and get German translations
- **Auto-generated Sentences**: Creates example sentences in both languages
- **Beautiful UI**: Consistent design with the vocabulary player

### 🎨 Design Features
- **Horizontal Navigation**: Top navigation bar with both features clearly visible
- **Glassmorphism Effects**: Modern translucent design with backdrop blur
- **Gradient Backgrounds**: Beautiful purple-blue gradient theme
- **Responsive Layout**: Works perfectly on desktop and mobile devices
- **Smooth Animations**: Hover effects and transitions throughout

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Pandas**: Data processing for vocabulary CSV files
- **CORS**: Cross-origin resource sharing enabled
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and development server
- **Axios**: HTTP client for API calls
- **CSS3**: Custom styling with modern features

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/amar030383/languageLearning.git
cd languageLearning
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv ../.venv

# Activate virtual environment (Linux/Mac)
source ../.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```
Backend will be running on `http://localhost:8000`

### 3. Frontend Setup
```bash
# Open new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
Frontend will be running on `http://localhost:3000`

### 4. Access the Application
Open your browser and go to `http://localhost:3000`

## 📁 Project Structure

```
GermanFastAPI/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx    # Navigation sidebar
│   │   │   ├── VocabularyPlayer.jsx  # Audio player component
│   │   │   └── WordTranslator.jsx    # Translation component
│   │   ├── App.jsx            # Main application component
│   │   ├── App.css            # Styling
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Global styles
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── node_modules/          # (gitignored)
├── german_audio/              # Audio files directory
├── SingeSheet.csv             # Vocabulary data
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Configuration

### Backend Configuration
- **Port**: 8000 (configurable in main.py)
- **CORS**: Enabled for `http://localhost:3000` and `http://localhost:5173`
- **Data Source**: `SingeSheet.csv` file with vocabulary data

### Frontend Configuration
- **Port**: 3000 (configurable in vite.config.js)
- **Proxy**: API calls to `/api/*` are proxied to `http://localhost:8000`
- **Development**: Hot reload enabled

## 📊 API Endpoints

### Vocabulary API
- **GET** `/api/vocabulary` - Get all vocabulary entries
- **HEAD** `/api/audio/{index}/{type}` - Check if audio file exists
- **GET** `/api/audio/{index}/{type}` - Serve audio files

### Translation API
- **POST** `/api/translate` - Translate English word to German

## 🎯 Usage Guide

### Vocabulary Player
1. Click the **🇩🇪 Vocabulary Player** tab in the top navigation
2. Click **▶ Play** to start audio playback
3. Use **🔄 Start AutoPlay** for continuous playback
4. Adjust **German sentence speed** with the slider
5. Navigate with **Previous/Next** buttons

### Word Translator
1. Click the **🔄 Word Translator** tab in the top navigation
2. Enter an English word in the input field
3. Click **🌐 Translate** to see the German translation
4. View auto-generated example sentences

## 🔧 Development

### Adding New Features
1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create new components in `src/components/`
3. **Styling**: Update `App.css` for consistent design

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend is ready for deployment as-is
```

## 🚨 Troubleshooting

### "Failed to load vocabulary data"
- Ensure backend server is running on port 8000
- Check that `SingeSheet.csv` exists and contains data
- Verify CORS configuration in backend

### Audio files not playing
- Check that audio files exist in `german_audio/` directory
- Ensure file names match the format expected by the API
- Check browser console for CORS or network errors

### Translation not working
- Verify backend server is running
- Check network connectivity
- Ensure API endpoint `/api/translate` is accessible

## 📝 Data Format

The `SingeSheet.csv` file should have the following columns:
- `german_word`: German vocabulary word
- `english_word`: English translation
- `german_sentence`: Example sentence in German
- `english_sentence`: Example sentence in English

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- German audio files for pronunciation practice
- FastAPI and React communities for excellent documentation
- Modern web development tools and libraries

---

**Happy Learning! 🇩🇪📚**
