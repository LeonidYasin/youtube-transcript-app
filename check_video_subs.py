import sys
from app.services.youtube import YouTubeService

def check_video(video_id, lang='ru'):
    print(f"\n{'='*50}")
    print(f"Проверка видео: https://www.youtube.com/watch?v={video_id}")
    print(f"Язык: {lang}")
    
    service = YouTubeService()
    
    # Пробуем получить субтитры
    print("\nПопытка получить субтитры...")
    text, error = service.get_subtitles(video_id, lang=lang)
    
    if text:
        print("✅ Субтитры успешно загружены!")
        print("\nПервые 500 символов:")
        print(text[:500] + "...")
        
        # Сохраняем в файл
        filename = f"{video_id}_{lang}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\nСубтитры сохранены в файл: {filename}")
        return True
    else:
        print(f"❌ Ошибка: {error}")
        return False

if __name__ == "__main__":
    # Устанавливаем кодировку консоли
    sys.stdout.reconfigure(encoding='utf-8')
    
    # ID первого видео, которое мы проверяли ранее
    video_id = "xXU4-tiX4Wk"
    
    # Сначала проверяем русские субтитры
    if not check_video(video_id, 'ru'):
        # Если русских нет, проверяем доступные языки
        print("\nПроверяем доступные языки...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            print("\nДоступные субтитры:")
            for transcript in transcript_list:
                print(f"- {transcript.language} ({transcript.language_code}): "
                      f"{'автоматические' if transcript.is_generated else 'ручные'}")
                
                if transcript.is_translatable:
                    print(f"  Можно перевести на: {', '.join([t.language for t in transcript.translation_languages])}")
                    
                    # Пробуем получить русский перевод
                    if 'ru' in [t.language_code for t in transcript.translation_languages]:
                        print("\nПробуем получить русский перевод...")
                        translated = transcript.translate('ru').fetch()
                        if translated:
                            text = '\n'.join([t['text'] for t in translated])
                            filename = f"{video_id}_ru_translated.txt"
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(text)
                            print(f"✅ Перевод сохранен в файл: {filename}")
                            
        except Exception as e:
            print(f"Ошибка при проверке доступных языков: {e}")
