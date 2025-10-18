import pandas as pd
from googletrans import Translator
from tqdm import tqdm
import time
import sys
from datetime import datetime

def translate_text(translator, text, src='en', dest='hi', retries=3):
    """Translate text with retry and error handling"""
    text = str(text).strip()
    if not text:
        return ""
    
    for attempt in range(retries):
        try:
            result = translator.translate(text, src=src, dest=dest)
            return result.text
        except Exception as e:
            if attempt == retries - 1:
                return f"ERROR: {e}"
            time.sleep(2)

def main():
    try:
        translator = Translator()

        # Create or clear log file
        with open("translation_log.txt", "w", encoding="utf-8") as f:
            f.write(f"Translation started at {datetime.now()}\n")

        # Load CSV file (use python engine and skip malformed lines)
        try:
            df = pd.read_csv("SingeSheet.csv", engine="python", on_bad_lines="skip")
            print(f"Loaded CSV with {len(df)} rows")
        except Exception as e:
            # If reading fails, write a clear log and exit
            with open("translation_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Failed to read SingeSheet.csv: {e}\n")
            print(f"Failed to read SingeSheet.csv: {e}")
            sys.exit(1)
        english_word_col = df.columns[1]
        english_sentence_col = df.columns[3]

        # Add columns if not already present
        if "Hindi Meaning" not in df.columns:
            df["Hindi Meaning"] = ""
        if "Hindi Sentence" not in df.columns:
            df["Hindi Sentence"] = ""

        # Translate English words
        print("\n🔤 Translating Words...")
        for index, row in tqdm(df.iterrows(), total=len(df)):
            if not df.at[index, "Hindi Meaning"]:
                hindi_meaning = translate_text(translator, row[english_word_col])
                df.at[index, "Hindi Meaning"] = hindi_meaning
                if index % 50 == 0 and index != 0:
                    df.to_excel("SingeSheet_with_Hindi.xlsx", index=False)
                    print(f"Progress saved at row {index}")

        # Translate English sentences
        print("\n📝 Translating Sentences...")
        for index, row in tqdm(df.iterrows(), total=len(df)):
            if not df.at[index, "Hindi Sentence"]:
                hindi_sentence = translate_text(translator, row[english_sentence_col])
                df.at[index, "Hindi Sentence"] = hindi_sentence
                if index % 50 == 0 and index != 0:
                    df.to_excel("SingeSheet_with_Hindi.xlsx", index=False)
                    print(f"Progress saved at row {index}")

        # Save final file
        output_file = "SingeSheet_with_Hindi.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Translation completed and saved as: {output_file}")

    except KeyboardInterrupt:
        print("\nProcess interrupted. Saving progress...")
        try:
            df.to_excel("SingeSheet_with_Hindi_interrupted.xlsx", index=False)
        except Exception:
            # If df is not available or saving fails, write a fallback log
            with open("translation_log.txt", "a", encoding="utf-8") as f:
                f.write("Process interrupted before any progress could be saved.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        try:
            df.to_excel("SingeSheet_with_Hindi_error.xlsx", index=False)
        except Exception:
            with open("translation_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Unexpected error and failed to save dataframe: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
