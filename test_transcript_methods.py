import requests
import json
from app.services.youtube import YouTubeService

# Инициализируем сервис
youtube_service = YouTubeService()

# Тестовый видео ID
TEST_VIDEO_ID = "tw9USlQh6jw"

async def test_youtube_transcript_api_new():
    print("\nTesting YouTube Transcript API (New)")
    try:
        result = await youtube_service._handle_new_api(TEST_VIDEO_ID, lang="ru")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")

async def test_youtube_transcript_api_old():
    print("\nTesting YouTube Transcript API (Old)")
    try:
        result = await youtube_service._handle_old_api(TEST_VIDEO_ID, lang="ru")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_yt_dlp():
    print("\nTesting yt-dlp")
    try:
        result = youtube_service._get_subtitles_with_ytdlp(TEST_VIDEO_ID, lang="ru")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    # Тестируем каждый метод по отдельности
    print(f"Testing video: https://www.youtube.com/watch?v={TEST_VIDEO_ID}")
    print("-" * 80)
    
    # Тестируем yt-dlp (синхронный метод)
    test_yt_dlp()
    
    # Тестируем API методы (асинхронные)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_youtube_transcript_api_new())
    loop.run_until_complete(test_youtube_transcript_api_old())
