"""
Generate missing audio files for German vocabulary.
This script creates audio files only for entries that are missing or have 0 bytes.
"""

import os
import pandas as pd
from gtts import gTTS
from pathlib import Path

def generate_missing_audio(csv_path: str, output_dir: str = "german_audio", start_index: int = 0) -> None:
    """
    Generate audio files for missing entries starting from a specific index.
    
    Args:
        csv_path: Path to the CSV file
        output_dir: Directory to save audio files
        start_index: Starting index for generating audio files
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Read the CSV file (no headers, 4 columns)
        df = pd.read_csv(csv_path, header=None, 
                        names=['german_word', 'english_word', 'german_sentence', 'english_sentence'])
        
        print(f"\n=== Generating Missing German Vocabulary Audio Files ===\n")
        print(f"Starting from index: {start_index}")
        print(f"Saving audio files to: {output_path.absolute()}\n")
        
        # Filter dataframe to start from the specified index
        df_subset = df.iloc[start_index:].copy()
        
        for index, row in df_subset.iterrows():
            german_word = str(row['german_word']).strip()
            english_word = str(row['english_word']).strip()
            
            if not german_word or not english_word or german_word == 'nan' or english_word == 'nan':
                continue
                
            # Create safe filenames
            safe_german = "".join(c if c.isalnum() else "_" for c in german_word)
            safe_english = "".join(c if c.isalnum() else "_" for c in english_word)
            
            # Create and save German word audio
            try:
                filename = f"{index:03d}_german_{safe_german[:20]}.mp3"
                filepath = output_path / filename
                
                # Check if file exists and has content
                if not filepath.exists() or filepath.stat().st_size == 0:
                    tts = gTTS(text=german_word, lang='de', slow=False)
                    tts.save(filepath)
                    print(f"Created: {filename}")
            except Exception as e:
                print(f"Error creating German word audio for '{german_word}': {e}")
            
            # Create and save English word audio
            try:
                filename = f"{index:03d}_english_{safe_english[:20]}.mp3"
                filepath = output_path / filename
                
                if not filepath.exists() or filepath.stat().st_size == 0:
                    tts = gTTS(text=english_word, lang='en', slow=False)
                    tts.save(filepath)
                    print(f"Created: {filename}")
            except Exception as e:
                print(f"Error creating English word audio for '{english_word}': {e}")
            
            # Check if there are sentences
            if 'german_sentence' in row and not pd.isna(row['german_sentence']):
                german_sentence = str(row['german_sentence']).strip()
                if german_sentence and german_sentence != 'nan':
                    try:
                        filename = f"{index:03d}_sentence_de_{safe_german[:15]}.mp3"
                        filepath = output_path / filename
                        
                        if not filepath.exists() or filepath.stat().st_size == 0:
                            tts = gTTS(text=german_sentence, lang='de', slow=False)
                            tts.save(filepath)
                            print(f"Created: {filename}")
                    except Exception as e:
                        print(f"Error creating German sentence audio: {e}")
            
            if 'english_sentence' in row and not pd.isna(row['english_sentence']):
                english_sentence = str(row['english_sentence']).strip()
                if english_sentence and english_sentence != 'nan':
                    try:
                        filename = f"{index:03d}_sentence_en_{safe_english[:15]}.mp3"
                        filepath = output_path / filename
                        
                        if not filepath.exists() or filepath.stat().st_size == 0:
                            tts = gTTS(text=english_sentence, lang='en', slow=False)
                            tts.save(filepath)
                            print(f"Created: {filename}")
                    except Exception as e:
                        print(f"Error creating English sentence audio: {e}")
            
            print()  # Add a blank line between entries
        
        print(f"\n=== Missing audio files generated successfully! ===")
        print(f"All audio files are in: {output_path.absolute()}")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate missing audio files for German vocabulary')
    parser.add_argument('file', nargs='?', default='SingeSheet.csv',
                       help='Path to the CSV file (default: SingeSheet.csv)')
    parser.add_argument('--output', '-o', default='german_audio',
                       help='Output directory for audio files (default: german_audio)')
    parser.add_argument('--start', '-s', type=int, default=480,
                       help='Starting index for generating audio files (default: 480)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
    else:
        generate_missing_audio(args.file, args.output, args.start)
