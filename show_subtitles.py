def show_subtitles(filename, max_lines=50):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"Первые {min(max_lines, len(lines))} строк файла {filename}:")
        print("-" * 80)
        
        for i, line in enumerate(lines[:max_lines], 1):
            print(f"{i:3}: {line.rstrip()}")
            
        if len(lines) > max_lines:
            print(f"\n... и ещё {len(lines) - max_lines} строк")
            
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    import sys
    
    # Устанавливаем кодировку вывода консоли
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Проверяем передан ли аргумент командной строки
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Используем последний созданный файл с субтитрами
        import glob
        import os
        
        subtitle_files = glob.glob("*_ru.txt") + glob.glob("*_ru_translated.txt")
        if not subtitle_files:
            print("Файлы субтитров не найдены в текущей директории.")
            sys.exit(1)
            
        # Сортируем по времени изменения (сначала новые)
        subtitle_files.sort(key=os.path.getmtime, reverse=True)
        filename = subtitle_files[0]
    
    show_subtitles(filename)
