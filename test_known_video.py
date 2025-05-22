from youtube_transcript_api import YouTubeTranscriptApi

def test_video(video_id, title):
    print(f"\nТестируем видео: {title}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    print("-" * 70)
    
    try:
        # Пытаемся получить список доступных языков
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Выводим информацию о доступных языках
        print("Доступные языки:")
        for transcript in transcript_list:
            print(f"- {transcript.language} ({transcript.language_code})")
            
            # Пробуем получить транскрипт
            try:
                transcript_text = transcript.fetch()
                print(f"  Успешно получен транскрипт, сегментов: {len(transcript_text)}")
                print("  Пример текста (первые 100 символов):")
                sample = " ".join([t['text'] for t in transcript_text[:3]])
                print(f"  {sample[:100]}...")
                return True
            except Exception as e:
                print(f"  Не удалось получить транскрипт: {str(e)}")
        
    except Exception as e:
        print(f"Ошибка при получении информации о транскриптах: {str(e)}")
    
    return False

if __name__ == "__main__":
    # Список популярных видео с высокой вероятностью наличия транскриптов
    test_videos = [
        {"id": "r5K1ZsoO1sU", "title": "Simon Sinek: How great leaders inspire action"},
        {"id": "iG9CE55wbtY", "title": "TED: The next outbreak? We're not ready"},
        {"id": "RcGyVTAoXEU", "title": "The secret to giving great feedback"},
        {"id": "Ks-_Mh1QhMc", "title": "Tim Urban: Inside the mind of a master procrastinator"}
    ]
    
    success_count = 0
    for video in test_videos:
        if test_video(video["id"], video["title"]):
            success_count += 1
    
    print(f"\nИтог: успешно получено транскриптов для {success_count} из {len(test_videos)} видео")
