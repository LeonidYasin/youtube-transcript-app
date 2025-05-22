from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def get_available_languages(video_id):
    """Получает список доступных языков для видео"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available = []
        
        # Добавляем оригинальные субтитры
        for transcript in transcript_list:
            lang_info = {
                'code': transcript.language_code,
                'name': transcript.language,
                'is_generated': transcript.is_generated,
                'is_translatable': transcript.is_translatable
            }
            available.append(lang_info)
            
            # Добавляем доступные переводы, если есть
            try:
                for translation in transcript.translation_languages:
                    # Используем атрибуты объекта вместо словаря
                    if hasattr(translation, 'language_code') and hasattr(translation, 'language'):
                        available.append({
                            'code': translation.language_code,
                            'name': translation.language,
                            'is_translation': True,
                            'original_language': transcript.language_code
                        })
            except Exception as e:
                logger.warning(f"Ошибка при получении переводов для {transcript.language_code}: {str(e)}")
                continue
                
        return available
    except Exception as e:
        logger.warning(f"Не удалось получить список языков: {str(e)}")
        return []

def detect_language(text):
    """Определяет язык текста по символам"""
    text = text.lower()
    # Проверяем наличие кириллических символов
    if any('а' <= c <= 'я' for c in text):
        return 'ru'
    # Проверяем наличие латинских символов
    if any('a' <= c <= 'z' for c in text):
        return 'en'
    # По умолчанию английский
    return 'en'

def fix_encoding(text):
    """
    Исправляет кодировку текста, который был неправильно закодирован
    
    Аргументы:
        text (str): Текст в неправильной кодировке
        
    Возвращает:
        str: Текст в правильной кодировке
    """
    if not text:
        return text
        
    try:
        # Пробуем UTF-16-LE (Little Endian) - основной случай для Windows
        try:
            # Пробуем интерпретировать как UTF-16-LE
            decoded = text.encode('latin1').decode('utf-16-le')
            # Проверяем, что получили разумный результат
            if any(c.isalpha() for c in decoded[:100] if c.isprintable()):
                return decoded
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            pass
            
        # Пробуем UTF-16-BE (Big Endian) на всякий случай
        try:
            decoded = text.encode('latin1').decode('utf-16-be')
            if any(c.isalpha() for c in decoded[:100] if c.isprintable()):
                return decoded
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
            
        # Пробуем исправить двойное кодирование
        try:
            fixed = text.encode('latin1').decode('utf-8')
            if any(c.isalpha() for c in fixed[:100] if c.isprintable()):
                return fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
                
        # Пробуем исправить кодировку из cp1251 в utf-8
        try:
            fixed = text.encode('cp1251').decode('utf-8', errors='strict')
            if any(c.isalpha() for c in fixed[:100] if c.isprintable()):
                return fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
            
        # Если ничего не помогло, возвращаем исходный текст
        return text
        
    except Exception as e:
        logger.warning(f"Не удалось исправить кодировку: {str(e)}")
        return text

def get_transcript(video_url, preferred_language='ru'):
    """
    Получает транскрипт видео на любом доступном языке
    
    Аргументы:
        video_url (str): URL видео на YouTube
        preferred_language (str): Предпочитаемый язык (например, 'ru', 'en'), по умолчанию 'ru'
        
    Возвращает:
        dict: Словарь с результатом
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"success": False, "error": "Неверный URL YouTube видео"}
            
        logger.info(f"Обработка видео ID: {video_id}, запрошенный язык: {preferred_language}")
        
        # Получаем список доступных транскриптов
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Получаем список всех доступных языков
        available_languages = [t.language_code for t in transcript_list]
        logger.info(f"Доступные языки: {available_languages}")
        
        # Пробуем найти русский транскрипт
        try:
            # Сначала ищем ручной русский
            transcript = transcript_list.find_manually_created_transcript(['ru'])
            logger.info("Найден ручной русский транскрипт")
        except:
            try:
                # Пробуем автоматический русский
                transcript = transcript_list.find_generated_transcript(['ru'])
                logger.info("Найден автоматический русский транскрипт")
            except:
                try:
                    # Пробуем переведенный русский
                    for t in transcript_list:
                        if t.is_translatable and 'ru' in [lang.language_code for lang in t.translation_languages]:
                            transcript = t.translate('ru')
                            logger.info("Найден переведенный русский транскрипт")
                            break
                    else:
                        # Если не нашли русский, берем английский
                        transcript = transcript_list.find_transcript(['en'])
                        logger.info("Русский не найден, используется английский")
                except Exception as e:
                    logger.warning(f"Не удалось найти русский или английский: {str(e)}")
                    # Берем первый доступный
                    transcript = next(iter(transcript_list))
                    logger.info(f"Используется первый доступный язык: {transcript.language_code}")
        
        # Получаем транскрипт
        transcript_data = transcript.fetch()
        transcript_text = "\n".join([t['text'] for t in transcript_data])
        
        # Если это перевод, добавляем пометку
        if hasattr(transcript, 'is_translation') and transcript.is_translation:
            transcript_text = f"[Переведено с {transcript.language}]\n\n{transcript_text}"
        
        logger.info(f"Успешно получен транскрипт на языке {transcript.language_code}, символов: {len(transcript_text)}")
                
                # Определяем язык текста
                detected_lang = detect_language(transcript_text[:1000]) if transcript_text else 'en'
                
                return transcript_text, detected_lang
                
            except Exception as e:
                logger.warning(f"Ошибка при получении транскрипта: {str(e)}")
                return None, None
        
        # Если запрошен конкретный язык, пробуем сначала его
        if preferred_language != 'any' and preferred_language in language_codes:
            logger.info(f"Попытка получить транскрипт для языка: {preferred_language}")
            
            transcript_text, detected_lang = get_transcript_text([preferred_language])
            if transcript_text:
                logger.info(f"Успешно получен транскрипт на запрошенном языке, символов: {len(transcript_text)}")
                return {
                    "success": True,
                    "video_id": video_id,
                    "transcript": transcript_text,
                    "language": preferred_language,
                    "available_languages": language_codes,
                    "error": None
                }
        
        # Пробуем получить транскрипт на английском, если доступен
        if 'en' in language_codes and preferred_language != 'en':
            logger.info("Попытка получить транскрипт на английском языке")
            
            transcript_text, detected_lang = get_transcript_text(['en'])
            if transcript_text:
                logger.info(f"Успешно получен английский транскрипт, символов: {len(transcript_text)}")
                return {
                    "success": True,
                    "video_id": video_id,
                    "transcript": transcript_text,
                    "language": 'en',
                    "available_languages": language_codes,
                    "error": None
                }
        
        # Пробуем получить транскрипт на любом доступном языке
        logger.info("Попытка получить транскрипт на любом доступном языке")
        
        transcript_text, detected_lang = get_transcript_text()
        if transcript_text:
            logger.info(f"Успешно получен транскрипт на языке {detected_lang}, символов: {len(transcript_text)}")
            return {
                "success": True,
                "video_id": video_id,
                "transcript": transcript_text,
                "language": detected_lang,
                "available_languages": language_codes,
                "error": None
            }
        
        # Если ничего не сработало, возвращаем ошибку с информацией о доступных языках
        error_msg = "Не удалось получить транскрипт"
        if available_languages:
            error_msg += f". Доступные языки: {', '.join([f"{l['code']} ({l['name']})" for l in available_languages])}"
        
        return {
            "success": False,
            "video_id": video_id,
            "transcript": None,
            "available_languages": language_codes,
            "error": error_msg
        }
        
    except Exception as e:
        error_msg = f"Ошибка при получении транскрипта: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "video_id": video_id if 'video_id' in locals() else None,
            "transcript": None,
            "error": error_msg
        }

def extract_video_id(url):
    """Извлекает ID видео из различных форматов URL YouTube"""
    import re
    
    # Список регулярных выражений для разных форматов URL
    patterns = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:embed\/|v=|\/)([a-zA-Z0-9_-]{11})',
        r'([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match and len(match.group(1)) == 11:  # YouTube ID всегда 11 символов
            return match.group(1)
    
    return None

# Пример использования
if __name__ == "__main__":
    # Тестируем на примере видео
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "https://youtu.be/dQw4w9WgXcQ",  # Короткая ссылка
        "https://www.youtube.com/embed/dQw4w9WgXcQ",  # Embed ссылка
    ]
    
    for url in test_urls:
        print(f"\nТестируем видео: {url}")
        result = get_transcript(url)
        
        if result["success"]:
            print(f"Успешно! Язык: {result['language']}, символов: {len(result['transcript'])}")
            print(f"Доступные языки: {', '.join(result['available_languages'])}")
            print("\nПервые 200 символов:")
            print("-" * 50)
            print(result['transcript'][:200] + ("..." if len(result['transcript']) > 200 else ""))
        else:
            print(f"Ошибка: {result['error']}")
            if result.get('available_languages'):
                print(f"Доступные языки: {', '.join(result['available_languages'])}")
