import sys
import json
from googletrans import Translator

def load_transcript(file_path):
    """Load transcript from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def translate_text(text, src='he', dest='ru'):
    """Translate text using Google Translate API."""
    try:
        translator = Translator()
        translation = translator.translate(text, src=src, dest=dest)
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation not available"

def main():
    # Get the first 500 characters of the transcript
    transcript = load_transcript('transcript.txt')
    if not transcript:
        print("No transcript found. Please run the test first to generate transcript.txt")
        return
    
    # Take first 500 characters or less if transcript is shorter
    sample_text = transcript[:500]
    
    # Split into lines and take first 5 non-empty lines
    lines = [line.strip() for line in sample_text.split('\n') if line.strip()]
    hebrew_sample = '\n'.join(lines[:5])
    
    # Translate to Russian
    russian_sample = translate_text(hebrew_sample)
    
    # Print results
    print("=== Иврит (оригинал) ===")
    print(hebrew_sample)
    print("\n=== Русский перевод ===")
    print(russian_sample)

if __name__ == "__main__":
    main()
