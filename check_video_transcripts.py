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
        # Получаем список всех доступных транскриптов
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Выводим информацию о каждом доступном транскрипте
        for transcript in transcript_list:
            print(f"\nЯзык: {transcript.language} ({transcript.language_code})")
            print(f"Является сгенерированным: {'Да' if transcript.is_generated else 'Нет'}")
            
            # Пробуем получить транскрипт
            try:
                transcript_text = transcript.fetch()
                print(f"Успешно получен транскрипт, количество сегментов: {len(transcript_text)}")
                print("\nПример текста (первые 200 символов):")
                sample = " ".join([t['text'] for t in transcript_text[:3]])
                print(sample[:200] + ("..." if len(sample) > 200 else ""))
            except Exception as e:
                print(f"Не удалось получить транскрипт: {str(e)}")
            
            # Показываем доступные переводы
            translation_languages = list(transcript.translation_languages)
            if translation_languages:
                print("\nДоступные переводы:")
                for lang in translation_languages:
                    print(f"- {lang['language']} ({lang['language_code']})")
                    
                    # Пробуем получить перевод
                    try:
                        translated = transcript.translate(lang['language_code']).fetch()
                        print(f"  Успешно получен перевод, сегментов: {len(translated)}")
                    except Exception as e:
                        print(f"  Не удалось получить перевод: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при проверке транскриптов: {str(e)}")
        return False

if __name__ == "__main__":
    # TED Talk: Simon Sinek - How great leaders inspire action
    video_id = "qp0HIF3SfI4"
    
    # Проверяем доступные транскрипты
    check_video_transcripts(video_id)
    
    # Попробуем другой формат ID (может помочь в некоторых случаях)
    if not check_video_transcripts(f"https://www.youtube.com/watch?v={video_id}"):
        print("\nПопробуем другой формат ID...")
        check_video_transcripts(video_id.replace("-", ""))
