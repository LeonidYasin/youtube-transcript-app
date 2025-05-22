import re
import os
from collections import Counter
from datetime import datetime

def clean_text(text):
    # Remove timestamps and formatting
    text = re.sub(r'\d{2}:\d{2}:\d{2}[\.\d]* --> \d{2}:\d{2}:\d{2}[\.\d]*.*\n', '', text)
    text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
    return text

def analyze_transcript(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic file info
        file_size = os.path.getsize(filename) / 1024  # KB
        lines = content.split('\n')
        line_count = len(lines)
        
        # Clean and process text
        clean_content = clean_text(content)
        words = re.findall(r'\b\w+\b', clean_content.lower())
        word_count = len(words)
        unique_words = len(set(words))
        
        # Most common words (excluding common Russian stop words)
        russian_stopwords = {'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'}
        word_freq = Counter([word for word in words if word not in russian_stopwords and len(word) > 2])
        
        # Estimate duration (assuming 150 words per minute)
        duration_min = round(word_count / 150, 1)
        
        # Extract key sentences (first few and last few)
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean_content) if s.strip()]
        first_sentences = sentences[:3]
        last_sentences = sentences[-3:] if len(sentences) > 3 else []
        
        # Main themes (based on most common nouns/verbs)
        themes = [word for word, _ in word_freq.most_common(10)]
        
        # Generate report
        report = f"""
=== Анализ транскрипта ===
Файл: {filename}
Размер: {file_size:.1f} KB
Количество строк: {line_count}
Количество слов: {word_count}
Уникальных слов: {unique_words}
Ориентировочная длительность: {duration_min} минут

Основные темы: {', '.join(themes)}

Начало текста:
- {'\n- '.join(first_sentences)}

Конец текста:
- {'\n- '.join(last_sentences) if last_sentences else 'Недостаточно данных'}

Самые частые слова (исключая предлоги и союзы):
"""
        
        # Add most common words
        for word, count in word_freq.most_common(15):
            report += f"- {word}: {count} раз\n"
            
        return report
        
    except Exception as e:
        return f"Ошибка при анализе файла: {str(e)}"

if __name__ == "__main__":
    import sys
    import glob
    
    # Set console encoding to UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Find the most recent subtitle file
    subtitle_files = glob.glob("*_ru.txt") + glob.glob("*_ru_translated.txt")
    
    if not subtitle_files:
        print("Файлы субтитров не найдены в текущей директории.")
    else:
        # Sort by modification time (newest first)
        subtitle_files.sort(key=lambda x: -os.path.getmtime(x))
        
        # Write analysis to a file to avoid console encoding issues
        output_file = "transcript_analysis.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(analyze_transcript(subtitle_files[0]))
        
        print(f"Анализ сохранен в файл: {output_file}")
        
        # Also show first 20 lines of the analysis
        with open(output_file, 'r', encoding='utf-8') as f:
            print("\nНачало анализа:")
            for i, line in enumerate(f):
                if i >= 40:  # Show first 40 lines
                    break
                print(line, end='')
        print("\n... (полный анализ смотрите в файле)")
