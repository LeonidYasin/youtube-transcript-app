def show_subtitle_lines(filename, start_line, end_line):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        print(f"Строки с {start_line} по {end_line} из файла {filename}:")
        print("-" * 80)
        
        # Adjust for 0-based index
        start = max(0, start_line - 1)
        end = min(len(lines), end_line)
        
        for i in range(start, end):
            # Skip empty lines and timestamp lines
            if lines[i] and not re.match(r'^\d{2}:\d{2}:\d{2}', lines[i]):
                print(f"{i+1:4}: {lines[i]}")
                
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    import sys
    import re
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
    
    # Show lines 80-100 from the most recent file
    show_subtitle_lines(subtitle_files[0], 80, 100)
