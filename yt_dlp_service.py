import yt_dlp
import logging
from typing import Dict, Any, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_transcript(video_url: str, lang: str = 'ru') -> Dict[str, Any]:
    """
    Получает транскрипт видео с помощью yt-dlp
    
    Аргументы:
        video_url (str): URL видео на YouTube
        lang (str): Код языка (например, 'ru', 'en')
        
    Возвращает:
        dict: Словарь с результатом
    """
    try:
        # Создаем опции для yt-dlp
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео
            info = ydl.extract_info(video_url, download=False)
            video_id = info.get('id')
            
            if not video_id:
                return {
                    "success": False,
                    "error": "Не удалось получить ID видео"
                }
            
            # Проверяем доступные субтитры
            subtitles = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            
            # Объединяем ручные и автоматические субтитры
            all_subs = {**subtitles, **auto_subs}
            
            if not all_subs:
                return {
                    "success": False,
                    "error": "Для этого видео нет доступных субтитров"
                }
            
            # Ищем запрошенный язык
            target_subs = all_subs.get(lang, [])
            
            if not target_subs:
                available_langs = list(all_subs.keys())
                return {
                    "success": False,
                    "error": f"Субтитры на языке '{lang}' не найдены",
                    "available_languages": available_langs
                }
            
            # Берем первый доступный формат субтитров
            sub_url = target_subs[0].get('url')
            if not sub_url:
                return {
                    "success": False,
                    "error": "Не удалось получить URL субтитров"
                }
            
            # Загружаем субтитры
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'outtmpl': 'subtitles/%(id)s.%(ext)s',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as sub_ydl:
                sub_info = sub_ydl.extract_info(sub_url, download=False)
                transcript = sub_info.get('data', '')
            
            return {
                "success": True,
                "video_id": video_id,
                "transcript": transcript,
                "language": lang,
                "is_generated": lang in auto_subs
            }
            
    except Exception as e:
        logger.error(f"Ошибка при получении транскрипта: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Ошибка при получении транскрипта: {str(e)}"
        }

if __name__ == "__main__":
    # Тестирование
    test_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    result = get_transcript(test_url, 'ru')
    
    if result.get('success'):
        print("Транскрипт успешно получен!")
        print(f"Язык: {result.get('language')}")
        print(f"Длина текста: {len(result.get('transcript', ''))} символов")
        print("\nПервые 500 символов:")
        print("-" * 50)
        print(result.get('transcript', '')[:500])
        print("-" * 50)
        
        # Сохраняем в файл
        with open('transcript_yt_dlp.txt', 'w', encoding='utf-8') as f:
            f.write(result.get('transcript', ''))
        print("\nПолный транскрипт сохранен в 'transcript_yt_dlp.txt'")
    else:
        print(f"Ошибка: {result.get('error')}")
