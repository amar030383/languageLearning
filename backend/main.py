"""
FastAPI Backend for German Vocabulary Audio Player

This module provides REST API endpoints to serve vocabulary data and audio files.
"""

import sqlite3
from datetime import datetime
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

class ExcludedWordRequest(BaseModel):
    word_index: int

class ExcludedWordResponse(BaseModel):
    word_index: int
    german_word: str
    english_word: str
    excluded_at: str = "1.0.0"

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

# Database setup
DB_PATH = BASE_DIR / "user_data.db"

def init_database():
    """Initialize SQLite database for user data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create excluded words table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS excluded_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_index INTEGER NOT NULL,
            german_word TEXT NOT NULL,
            english_word TEXT NOT NULL,
            excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(word_index)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

def load_vocabulary_data() -> pd.DataFrame:
    """
    Load vocabulary data from CSV file.
    
    Returns:
        DataFrame containing vocabulary data
    """
    try:
        # Try to read CSV assuming it already has headers (preferred)
        df_try = pd.read_csv(CSV_PATH)

        expected_cols = ['german_word', 'english_word', 'german_sentence', 'english_sentence', 'hindi_word', 'hindi_sentence']

        # If the expected columns are present, use this dataframe. Otherwise fall back to reading without header.
        if set(expected_cols).issubset(set(df_try.columns)):
            df = df_try
        else:
            # No header present — read without header and assign canonical names for the first 6 columns.
            df = pd.read_csv(
                CSV_PATH,
                header=None,
                names=expected_cols,
                usecols=range(6),
                dtype=str,
            )

        # Ensure string values and strip whitespace
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

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
    Get all vocabulary entries, excluding words marked as learned.

    Returns:
        List of vocabulary entries with index and words (excluding learned words)
    """
    df = load_vocabulary_data()

    # Get excluded word indices
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT word_index FROM excluded_words')
    excluded_indices = {row[0] for row in cursor.fetchall()}
    conn.close()

    vocabulary_list = []
    for index, row in df.iterrows():
        # Skip excluded words
        if index in excluded_indices:
            continue

        german_word = str(row['german_word']).strip()
        english_word = str(row['english_word']).strip()
        german_sentence = str(row['german_sentence']).strip()
        english_sentence = str(row['english_sentence']).strip()
        # Optional Hindi fields (may be absent or NaN)
        hindi_word = str(row['hindi_word']).strip() if 'hindi_word' in row.index else ''
        hindi_sentence = str(row['hindi_sentence']).strip() if 'hindi_sentence' in row.index else ''

        if german_word and english_word and german_word != 'nan' and english_word != 'nan':
            vocabulary_list.append({
                "index": index,
                "german_word": german_word,
                "english_word": english_word,
                "german_sentence": german_sentence,
                "english_sentence": english_sentence,
                "hindi_word": hindi_word,
                "hindi_sentence": hindi_sentence
            })

    random.shuffle(vocabulary_list)  # <-- Shuffle the list here

    return vocabulary_list

@app.get("/api/excluded-words")
async def get_excluded_words() -> List[Dict[str, Any]]:
    """
    Get all excluded words.

    Returns:
        List of excluded word entries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT word_index, german_word, english_word, excluded_at FROM excluded_words ORDER BY excluded_at DESC')
    rows = cursor.fetchall()

    excluded_words = []
    for row in rows:
        excluded_words.append({
            "word_index": row[0],
            "german_word": row[1],
            "english_word": row[2],
            "excluded_at": row[3]
        })

    conn.close()
    return excluded_words


@app.get("/api/csv-headers")
async def csv_headers() -> List[str]:
    """
    Return the CSV column headers detected/used when loading the vocabulary CSV.
    """
    df = load_vocabulary_data()
    return list(df.columns)


@app.get("/api/vocabulary/full")
async def get_vocabulary_full() -> List[Dict[str, Any]]:
    """
    Return the full CSV rows (all columns) as a list of dicts. Excluded words are filtered out the same way as `/api/vocabulary`.
    """
    df = load_vocabulary_data()

    # Get excluded word indices
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT word_index FROM excluded_words')
    excluded_indices = {row[0] for row in cursor.fetchall()}
    conn.close()

    rows: List[Dict[str, Any]] = []
    for index, row in df.iterrows():
        if index in excluded_indices:
            continue

        # Convert the entire row to a dict, ensure str values
        row_dict = {col: (None if pd.isna(row[col]) else str(row[col]).strip()) for col in df.columns}
        row_dict["index"] = int(index)
        rows.append(row_dict)

    return rows

@app.post("/api/excluded-words")
async def add_excluded_word(request: ExcludedWordRequest) -> Dict[str, str]:
    """
    Add a word to the excluded list.

    Args:
        request: Request with word index to exclude

    Returns:
        Success message
    """
    word_index = request.word_index

    # Get the word details from vocabulary
    df = load_vocabulary_data()
    if word_index < 0 or word_index >= len(df):
        raise HTTPException(status_code=404, detail="Word not found")

    row = df.iloc[word_index]
    german_word = str(row['german_word']).strip()
    english_word = str(row['english_word']).strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO excluded_words (word_index, german_word, english_word, excluded_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (word_index, german_word, english_word))

        conn.commit()
        conn.close()

        return {"message": f"Word '{german_word}' ({english_word}) added to excluded list"}

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error adding excluded word: {str(e)}")

@app.delete("/api/excluded-words/{word_index}")
async def remove_excluded_word(word_index: int) -> Dict[str, str]:
    """
    Remove a word from the excluded list.

    Args:
        word_index: Index of the word to remove from excluded list

    Returns:
        Success message
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM excluded_words WHERE word_index = ?', (word_index,))
        conn.commit()

        if cursor.rowcount > 0:
            conn.close()
            return {"message": f"Word with index {word_index} removed from excluded list"}
        else:
            conn.close()
            raise HTTPException(status_code=404, detail="Excluded word not found")

    except HTTPException:
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error removing excluded word: {str(e)}")

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
    hindi_word = str(row['hindi_word']).strip() if 'hindi_word' in row.index else ''
    hindi_sentence = str(row['hindi_sentence']).strip() if 'hindi_sentence' in row.index else ''
    
    return {
        "index": index,
        "german_word": german_word,
        "english_word": english_word,
        "german_sentence": german_sentence,
        "english_sentence": english_sentence,
        "hindi_word": hindi_word,
        "hindi_sentence": hindi_sentence
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
