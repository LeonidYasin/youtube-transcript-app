import sys
from app.services.youtube import YouTubeService

# Устанавливаем кодировку консоли
sys.stdout.reconfigure(encoding='utf-8')

def test_video(video_id, lang='ru'):
    print(f"\n{'='*50}")
    print(f"Тестирование видео: https://www.youtube.com/watch?v={video_id}")
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
    else:
        print(f"❌ Ошибка: {error}")
        
        # Пробуем получить список доступных языков
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
                    
        except Exception as e:
            print(f"Ошибка при проверке доступных языков: {e}")

if __name__ == "__main__":
    # Тестируем несколько видео
    video_ids = [
        "xXU4-tiX4Wk",  # Видео рава Гинцбурга на иврите
        "frU7zeWE5FU",  # Видео с английскими субтитрами
        "jSS_MT5sxdA"   # Другое видео с канала
    ]
    
    for video_id in video_ids:
        test_video(video_id, 'ru')
        
    print("\nГотово! Проверьте файлы с субтитрами в текущей директории.")
