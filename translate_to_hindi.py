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

        # Load CSV file
        df = pd.read_csv("SingeSheet.csv")
        print(f"Loaded CSV with {len(df)} rows")
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
        df.to_excel("SingeSheet_with_Hindi_interrupted.xlsx", index=False)
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        df.to_excel("SingeSheet_with_Hindi_error.xlsx", index=False)
        sys.exit(1)

if __name__ == "__main__":
    main()
