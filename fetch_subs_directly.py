import requests
import json
import re
from urllib.parse import parse_qs, urlparse

def get_video_id(url):
    """Извлекает ID видео из URL YouTube"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*$',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_with_encoding_fix(video_id, lang='ru'):
    """Получает транскрипт с исправлением кодировки"""
    try:
        # Получаем информацию о доступных субтитрах
        url = f"https://youtube.com/watch?v={video_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Ошибка при загрузке страницы: {response.status_code}")
            return None
            
        # Ищем JSON с информацией о субтитрах
        match = re.search(r'"captions":(\{.*?\})', response.text)
        if not match:
            print("Не удалось найти информацию о субтитрах")
            return None
            
        captions_data = json.loads(match.group(1) + '}')
        
        # Ищем URL базового манифеста субтитров
        base_url = captions_data.get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [{}])[0].get('baseUrl')
        if not base_url:
            print("Не удалось найти URL субтитров")
            return None
            
        # Загружаем субтитры
        subs_response = requests.get(base_url)
        if subs_response.status_code != 200:
            print(f"Ошибка при загрузке субтитров: {subs_response.status_code}")
            return None
            
        # Пробуем разные кодировки
        try:
            # Пробуем UTF-8
            text = subs_response.text
            if any(ord(c) > 127 for c in text):
                # Если есть не-ASCII символы, пробуем windows-1251
                try:
                    text = subs_response.content.decode('windows-1251')
                except UnicodeDecodeError:
                    # Если не сработало, оставляем как есть
                    pass
            
            # Сохраняем в файл
            output_file = f'subs_{video_id}_{lang}.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
                
            print(f"Субтитры сохранены в {output_file}")
            
            # Извлекаем только текст из XML
            text_only = '\n'.join(re.findall(r'<text[^>]*>([^<]+)</text>', text))
            text_file = f'transcript_{video_id}_{lang}.txt'
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_only)
                
            print(f"Текст субтитров сохранен в {text_file}")
            return text_only
            
        except Exception as e:
            print(f"Ошибка при обработке субтитров: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

if __name__ == "__main__":
    # Тестируем на видео Simon Sinek
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    video_id = get_video_id(video_url)
    
    if video_id:
        print(f"ID видео: {video_id}")
        text = get_transcript_with_encoding_fix(video_id, 'ru')
        
        if text:
            print("\nПервые 500 символов:")
            print("-" * 50)
            print(text[:500])
            print("-" * 50)
    else:
        print("Не удалось извлечь ID видео из URL")
