from youtube_transcript_api import YouTubeTranscriptApi
import json

def get_raw_transcript(video_id, language='ru'):
    print(f"Получаем транскрипцию для видео {video_id} на языке {language}")
    print("=" * 80)
    
    try:
        # Получаем сырые данные транскрипции
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=[language],
            preserve_formatting=True
        )
        
        print(f"\nПолучено {len(transcript)} сегментов")
        print("\nПервые 5 сегментов:")
        for i, segment in enumerate(transcript[:5]):
            print(f"{i+1}. {segment}")
        
        # Выводим информацию о кодировке первого сегмента
        if transcript:
            first_segment = transcript[0]
            text = first_segment.get('text', '')
            print(f"\nПервый сегмент (первые 50 байт в hex):")
            print(' '.join(f'{b:02x}' for b in text.encode('utf-8')[:50]))
            print(f"\nТекст первого сегмента: {text}")
        
        return transcript
        
    except Exception as e:
        print(f"Ошибка при получении транскрипции: {str(e)}")
        return None

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"
    language = "ru"
    transcript = get_raw_transcript(video_id, language)
