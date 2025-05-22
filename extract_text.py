import re

def extract_text_from_srt(filename, max_paragraphs=10):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove timestamps and formatting
        text = re.sub(r'\d{2}:\d{2}:\d{2}[\.\d]* --> \d{2}:\d{2}:\d{2}[\.\d]*.*\n', '', content)
        text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
        text = re.sub(r'\n{3,}', '\n\n', text)  # Normalize newlines
        
        # Split into paragraphs and clean up
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        print(f"Текст из файла {filename} (первые {min(max_paragraphs, len(paragraphs))} абзацев):\n")
        print("-" * 80)
        
        for i, p in enumerate(paragraphs[:max_paragraphs], 1):
            # Clean up and format each paragraph
            p = re.sub(r'\s+', ' ', p).strip()
            print(f"{p}\n")
            
        if len(paragraphs) > max_paragraphs:
            print(f"\n... и ещё {len(paragraphs) - max_paragraphs} абзацев")
            
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    import sys
    import glob
    import os
    
    # Set console encoding
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Find subtitle files
    subtitle_files = glob.glob("*_ru.txt") + glob.glob("*_ru_translated.txt")
    
    if not subtitle_files:
        print("Файлы субтитров не найдены в текущей директории.")
        sys.exit(1)
        
    # Sort by modification time (newest first)
    subtitle_files.sort(key=lambda x: -os.path.getmtime(x))
    
    # Process the most recent file
    extract_text_from_srt(subtitle_files[0])
