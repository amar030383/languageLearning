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

        if german_word and english_word and german_word != 'nan' and english_word != 'nan':
            vocabulary_list.append({
                "index": index,
                "german_word": german_word,
                "english_word": english_word,
                "german_sentence": german_sentence,
                "english_sentence": english_sentence
            })

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
    Translate English word or sentence to German using external API.

    Args:
        request: Translation request with English word or sentence

    Returns:
        Translation response with German translation and examples
    """
    english_input = request.english_word.strip()

    try:
        # Use LibreTranslate API for translation
        german_translation = await translate_with_libretranslate(english_input)

        # Generate example sentences using the original input and translation
        english_sentence = english_input
        german_sentence = german_translation

        return TranslationResponse(
            german_word=german_translation,
            english_sentence=english_sentence,
            german_sentence=german_sentence
        )

    except Exception as e:
        # Fallback: return input as-is if translation fails
        return TranslationResponse(
            german_word=f"Translation service unavailable: {english_input}",
            english_sentence=english_input,
            german_sentence=f"Übersetzung nicht verfügbar: {english_input}"
        )


async def translate_with_libretranslate(text: str) -> str:
    """
    Translate text using LibreTranslate API with fallback to local translation.

    Args:
        text: Text to translate

    Returns:
        Translated text in German
    """
    try:
        # LibreTranslate API endpoint (free public instance)
        url = "https://libretranslate.com/translate"

        payload = {
            "q": text,
            "source": "en",
            "target": "de",
            "format": "text"
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            translated_text = result.get("translatedText", text)

            # Check if translation was successful (not just returning original text)
            if translated_text.strip().lower() != text.strip().lower():
                return translated_text
            else:
                # API returned original text, use fallback
                return translate_with_fallback(text)
        else:
            # If API fails, use fallback
            return translate_with_fallback(text)

    except Exception as e:
        # If API is unavailable, use fallback
        return translate_with_fallback(text)


def translate_with_fallback(text: str) -> str:
    """
    Fallback translation using pattern matching and word-by-word translation.

    Args:
        text: Text to translate

    Returns:
        Translated text in German using fallback method
    """
    # Common phrase patterns for better sentence translation
    phrase_patterns = {
        "hello how are you": "hallo wie geht es dir",
        "how are you": "wie geht es dir",
        "i am fine": "mir geht es gut",
        "i am good": "mir geht es gut",
        "thank you": "danke",
        "goodbye": "tschüss",
        "good morning": "guten morgen",
        "good afternoon": "guten tag",
        "good evening": "guten abend",
        "good night": "gute nacht",
        "i love you": "ich liebe dich",
        "i miss you": "du fehlst mir",
        "i need help": "ich brauche hilfe",
        "where is": "wo ist",
        "how much": "wie viel",
        "what time": "wie spät",
        "i don't understand": "ich verstehe nicht",
        "please speak slowly": "bitte sprechen sie langsam",
        "can you help me": "können sie mir helfen",
        "i am hungry": "ich bin hungrig",
        "i am thirsty": "ich bin durstig",
        "i am tired": "ich bin müde",
        "i am happy": "ich bin glücklich",
        "i am sad": "ich bin traurig",
        "this is": "das ist",
        "that is": "das ist",
        "here is": "hier ist",
        "there is": "dort ist",
        "i have": "ich habe",
        "i want": "ich möchte",
        "i like": "ich mag",
        "i don't like": "ich mag nicht",
        "do you speak english": "sprechen sie englisch",
        "do you speak german": "sprechen sie deutsch",
        "i speak a little german": "ich spreche ein bisschen deutsch",
        "how old are you": "wie alt bist du",
        "where are you from": "woher kommst du",
        "i am from": "ich komme aus",
        "what do you do": "was machst du beruflich",
        "i am a student": "ich bin student",
        "i am a teacher": "ich bin lehrer",
        "i work at": "ich arbeite bei",
        "i live in": "ich wohne in",
        "how is the weather": "wie ist das wetter",
        "it is sunny": "es ist sonnig",
        "it is raining": "es regnet",
        "it is cold": "es ist kalt",
        "it is hot": "es ist heiß",
        "i am going to": "ich gehe zu",
        "i am coming from": "ich komme von",
        "see you later": "bis später",
        "see you tomorrow": "bis morgen",
        "take care": "pass auf dich auf",
        "have a good day": "hab einen schönen tag",
        "have a good night": "hab eine gute nacht",
        "see you soon": "bis bald",
        "i am sorry": "es tut mir leid",
        "excuse me": "entschuldigung",
        "nice to meet you": "freut mich dich kennenzulernen",
        "what is your name": "wie heißt du",
        "my name is": "ich heiße",
        "i am": "ich bin",
        "you are": "du bist",
        "he is": "er ist",
        "she is": "sie ist",
        "we are": "wir sind",
        "they are": "sie sind"
    }

    # Check for exact phrase matches first
    text_lower = text.lower().strip()
    if text_lower in phrase_patterns:
        return phrase_patterns[text_lower]

    # Word-by-word translation with improved vocabulary
    word_translations = {
        "house": "Haus", "home": "Zuhause", "car": "Auto", "dog": "Hund", "cat": "Katze",
        "book": "Buch", "table": "Tisch", "chair": "Stuhl", "water": "Wasser", "food": "Essen",
        "computer": "Computer", "phone": "Telefon", "music": "Musik", "school": "Schule",
        "friend": "Freund", "family": "Familie", "work": "Arbeit", "time": "Zeit", "day": "Tag",
        "night": "Nacht", "good": "gut", "bad": "schlecht", "big": "groß", "small": "klein",
        "hot": "heiß", "cold": "kalt", "happy": "glücklich", "sad": "traurig", "tired": "müde",
        "beautiful": "schön", "fast": "schnell", "slow": "langsam", "new": "neu", "old": "alt",
        "hello": "hallo", "goodbye": "tschüss", "yes": "ja", "no": "nein", "please": "bitte",
        "thank": "danke", "sorry": "entschuldigung", "welcome": "willkommen", "test": "Test",
        "this": "dieses", "that": "jenes", "now": "jetzt", "here": "hier", "there": "dort",
        "let's": "lassen wir", "let us": "lassen wir", "i": "ich", "you": "du", "he": "er",
        "she": "sie", "we": "wir", "they": "sie", "me": "mir", "my": "mein", "your": "dein",
        "his": "sein", "her": "ihr", "our": "unser", "their": "ihr", "the": "der/die/das",
        "a": "ein/eine", "an": "ein/eine", "is": "ist", "are": "sind", "was": "war",
        "were": "waren", "will": "werde", "would": "würde", "can": "kann", "could": "könnte",
        "should": "sollte", "may": "darf", "might": "könnte", "must": "muss", "have": "habe",
        "has": "hat", "had": "hatte", "do": "tue", "does": "tut", "did": "tat", "make": "mache",
        "made": "machte", "go": "gehe", "went": "ging", "come": "komme", "came": "kam",
        "see": "sehe", "saw": "sah", "look": "schaue", "watch": "schaue", "read": "lese",
        "write": "schreibe", "learn": "lerne", "teach": "lehre", "help": "helfe", "play": "spiele",
        "work": "arbeite", "buy": "kaufe", "sell": "verkaufe", "give": "gebe", "take": "nehme",
        "eat": "esse", "drink": "trinke", "sleep": "schlafe", "run": "laufe", "walk": "gehe",
        "talk": "spreche", "listen": "höre", "hear": "höre", "speak": "spreche", "say": "sage",
        "tell": "sage", "ask": "frage", "answer": "antworte", "know": "weiß", "think": "denke",
        "understand": "verstehe", "remember": "erinnere", "forget": "vergesse", "love": "liebe",
        "like": "mag", "hate": "hasse", "want": "möchte", "need": "brauche", "find": "finde",
        "lose": "verliere", "win": "gewinne", "start": "beginne", "finish": "beende", "stop": "stoppe",
        "open": "öffne", "close": "schließe", "begin": "beginne", "end": "ende", "live": "lebe",
        "die": "sterbe", "kill": "töte", "save": "rette", "keep": "behalte", "hold": "halte",
        "bring": "bringe", "carry": "trage", "send": "sende", "receive": "empfange", "get": "bekomme",
        "put": "lege", "set": "setze", "place": "stelle", "sit": "sitze", "stand": "stehe",
        "lie": "liege", "build": "baue", "cook": "koche", "clean": "putze", "wash": "wasche",
        "drive": "fahre", "fly": "fliege", "swim": "schwimme", "jump": "springe", "dance": "tanze",
        "sing": "singe", "draw": "zeichne", "paint": "male", "write": "schreibe", "read": "lese",
        "study": "studiere", "teach": "lehre", "travel": "reise", "visit": "besuche", "meet": "treffe",
        "call": "rufe", "text": "schreibe", "email": "maile", "message": "nachrichte", "chat": "chatte"
    }

    words = text.split()
    translated_words = []

    for word in words:
        # Remove punctuation for translation
        clean_word = word.strip('.,!?').lower()
        german_word = word_translations.get(clean_word, clean_word.title())

        # Keep original capitalization for proper nouns or first words
        if word.istitle() or (word == words[0] and word[0].isupper()):
            german_word = german_word.capitalize()

        translated_words.append(german_word)

    return ' '.join(translated_words)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
