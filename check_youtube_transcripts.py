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

def check_video_transcripts(video_id):
    """Проверяет доступные транскрипты для видео"""
    print(f"\nПроверка доступных транскриптов для видео ID: {video_id}")
    print("-" * 70)
    
    try:
        # Пытаемся получить список всех доступных транскриптов
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print(f"Найдено транскриптов: {len(list(transcript_list._translation_languages))}")
        
        # Выводим информацию о каждом доступном транскрипте
        for transcript in transcript_list:
            print(f"\nЯзык: {transcript.language} ({transcript.language_code})")
            print(f"Автоматически сгенерирован: {'Да' if transcript.is_generated else 'Нет'}")
            
            # Пробуем получить транскрипт
            try:
                transcript_text = transcript.fetch()
                print(f"Успешно получен транскрипт, сегментов: {len(transcript_text)}")
                print("\nПример текста (первые 200 символов):")
                sample = " ".join([t['text'] for t in transcript_text[:3]])
                print(sample[:200] + ("..." if len(sample) > 200 else ""))
                
                # Если это не английский, попробуем получить английский перевод
                if transcript.language_code != 'en':
                    try:
                        translated = transcript.translate('en').fetch()
                        print(f"\nПеревод на английский (первые 200 символов):")
                        sample_en = " ".join([t['text'] for t in translated[:3]])
                        print(sample_en[:200] + ("..." if len(sample_en) > 200 else ""))
                    except Exception as e:
                        print(f"Не удалось получить перевод на английский: {str(e)}")
                        
            except Exception as e:
                print(f"Не удалось получить транскрипт: {str(e)}")
            
            # Показываем доступные переводы
            try:
                translation_languages = list(transcript.translation_languages)
                if translation_languages:
                    print("\nДоступные переводы:")
                    for lang in translation_languages:
                        print(f"- {lang['language']} ({lang['language_code']})")
            except Exception as e:
                print(f"Ошибка при получении списка переводов: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при проверке транскриптов: {str(e)}")
        return False

if __name__ == "__main__":
    # TED Talk: Simon Sinek - How great leaders inspire action
    video_id = "qp0HIF3SfI4"
    
    # Проверяем доступные транскрипты
    check_video_transcripts(video_id)
