from youtube_transcript_api import YouTubeTranscriptApi

def get_video_transcript(video_id):
    """Получает транскрипт видео напрямую"""
    try:
        # Пытаемся получить английский транскрипт
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return {
            'success': True,
            'language': 'en',
            'transcript': ' '.join([t['text'] for t in transcript]),
            'segments': len(transcript)
        }
    except Exception as e:
        # Если не получилось, пробуем получить любой доступный
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return {
                'success': True,
                'language': 'auto',
                'transcript': ' '.join([t['text'] for t in transcript]),
                'segments': len(transcript)
            }
        except Exception as e2:
            return {
                'success': False,
                'error': str(e2)
            }

if __name__ == "__main__":
    # TED Talk: Simon Sinek - How great leaders inspire action
    video_id = "qp0HIF3SfI4"
    
    print(f"Попытка получить транскрипт для видео: https://www.youtube.com/watch?v={video_id}")
    
    result = get_video_transcript(video_id)
    
    if result['success']:
        print(f"\nУспешно получен транскрипт на языке: {result['language']}")
        print(f"Количество сегментов: {result['segments']}")
        print("\nПервые 500 символов транскрипта:")
        print("-" * 50)
        print(result['transcript'][:500] + ("..." if len(result['transcript']) > 500 else ""))
    else:
        print(f"\nНе удалось получить транскрипт: {result['error']}")
        
        # Показываем доступные языки
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("\nДоступные языки:")
            for transcript in transcript_list:
                print(f"- {transcript.language} ({transcript.language_code})")
        except Exception as e:
            print(f"Не удалось получить список доступных языков: {str(e)}")
