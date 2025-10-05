"""
FastAPI Backend for German Vocabulary Audio Player

This module provides REST API endpoints to serve vocabulary data and audio files.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Dict, Any
import os
import random
from pydantic import BaseModel
import pandas as pd

class TranslationRequest(BaseModel):
    english_word: str

class TranslationResponse(BaseModel):
    german_word: str
    english_sentence: str
    german_sentence: str

app = FastAPI(title="German Vocabulary API", version="1.0.0")

# CORS middleware to allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / "SingeSheet.csv"
AUDIO_DIR = BASE_DIR / "german_audio"


def load_vocabulary_data() -> pd.DataFrame:
    """
    Load vocabulary data from CSV file.
    
    Returns:
        DataFrame containing vocabulary data
    """
    try:
        df = pd.read_csv(
            CSV_PATH,
            header=None,
            names=['german_word', 'english_word', 'german_sentence', 'english_sentence']
        )
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading vocabulary data: {str(e)}")


def create_safe_filename(text: str) -> str:
    """
    Create a safe filename from text.
    
    Args:
        text: Input text to convert
        
    Returns:
        Safe filename string
    """
    return "".join(c if c.isalnum() else "_" for c in text)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    return {"message": "German Vocabulary API"}


@app.get("/api/vocabulary")
async def get_vocabulary() -> List[Dict[str, Any]]:
    """
    Get all vocabulary entries.
    
    Returns:
        List of vocabulary entries with index and words
    """
    df = load_vocabulary_data()
    
    vocabulary_list = []
    for index, row in df.iterrows():
        german_word = str(row['german_word']).strip()
        english_word = str(row['english_word']).strip()
        german_sentence = str(row['german_sentence']).strip()
        english_sentence = str(row['english_sentence']).strip()
        
        if german_word and english_word and german_word != 'nan' and english_word != 'nan':
            vocabulary_list.append({
                "index": index,
                "german_word": german_word,
                "english_word": english_word,
                "german_sentence": german_sentence,
                "english_sentence": english_sentence
            })
    
    return vocabulary_list


@app.get("/api/vocabulary/{index}")
async def get_vocabulary_item(index: int) -> Dict[str, Any]:
    """
    Get a specific vocabulary entry by index.
    
    Args:
        index: Index of the vocabulary entry
        
    Returns:
        Vocabulary entry details
    """
    df = load_vocabulary_data()
    
    if index < 0 or index >= len(df):
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")
    
    row = df.iloc[index]
    german_word = str(row['german_word']).strip()
    english_word = str(row['english_word']).strip()
    german_sentence = str(row['german_sentence']).strip()
    english_sentence = str(row['english_sentence']).strip()
    
    return {
        "index": index,
        "german_word": german_word,
        "english_word": english_word,
        "german_sentence": german_sentence,
        "english_sentence": english_sentence
    }


@app.api_route("/api/audio/{index}/{audio_type}", methods=["GET", "HEAD"])
async def get_audio(index: int, audio_type: str) -> FileResponse:
    """
    Get audio file for a specific vocabulary entry.
    
    Args:
        index: Index of the vocabulary entry
        audio_type: Type of audio (german_word, english_word, german_sentence, english_sentence)
        
    Returns:
        Audio file
    """
    df = load_vocabulary_data()
    
    if index < 0 or index >= len(df):
        raise HTTPException(status_code=404, detail="Vocabulary entry not found")
    
    row = df.iloc[index]
    german_word = str(row['german_word']).strip()
    english_word = str(row['english_word']).strip()
    
    safe_german = create_safe_filename(german_word)
    safe_english = create_safe_filename(english_word)
    
    # Determine the audio file path based on type
    audio_file_map = {
        "german_word": AUDIO_DIR / f"{index:03d}_german_{safe_german[:20]}.mp3",
        "english_word": AUDIO_DIR / f"{index:03d}_english_{safe_english[:20]}.mp3",
        "german_sentence": AUDIO_DIR / f"{index:03d}_sentence_de_{safe_german[:15]}.mp3",
        "english_sentence": AUDIO_DIR / f"{index:03d}_sentence_en_{safe_english[:15]}.mp3"
    }
    
    if audio_type not in audio_file_map:
        raise HTTPException(status_code=400, detail="Invalid audio type")
    
    audio_file = audio_file_map[audio_type]
    
    if not audio_file.exists() or audio_file.stat().st_size == 0:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        audio_file,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"inline; filename={audio_file.name}"}
    )


@app.post("/api/translate")
async def translate_word(request: TranslationRequest) -> TranslationResponse:
    """
    Translate English word to German and generate example sentences.
    
    Args:
        request: Translation request with English word
        
    Returns:
        Translation response with German word and sentences
    """
    english_word = request.english_word.strip().lower()
    
    # Simple translation mapping for common words
    translation_map = {
        "house": "Haus",
        "book": "Buch",
        "table": "Tisch",
        "chair": "Stuhl",
        "water": "Wasser",
        "food": "Essen",
        "money": "Geld",
        "time": "Zeit",
        "day": "Tag",
        "night": "Nacht",
        "city": "Stadt",
        "work": "Arbeit",
        "person": "Mensch",
        "man": "Mann",
        "woman": "Frau",
        "child": "Kind",
        "parents": "Eltern",
        "brother": "Bruder",
        "sister": "Schwester",
        "family": "Familie"
    }
    
    german_word = translation_map.get(english_word, f"{english_word.title()} (translation needed)")
    
    # Generate example sentences
    english_sentence = f"I see a {english_word}."
    german_sentence = f"Ich sehe ein {german_word}."
    
    return TranslationResponse(
        german_word=german_word,
        english_sentence=english_sentence,
        german_sentence=german_sentence
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
