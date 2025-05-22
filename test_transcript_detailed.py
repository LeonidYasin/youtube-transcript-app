import requests
import json
import sys

async def test_transcript_api():
    # Set default encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    video_id = "tw9USlQh6jw"
    test_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print("\nTesting YouTube Transcript API Methods")
    print("=" * 80)
    print(f"Testing video: {test_url}")
    print("-" * 80)
    
    # Test yt-dlp
    print("\nTesting yt-dlp method...")
    try:
        from app.services.youtube import YouTubeService
        youtube_service = YouTubeService()
        result = youtube_service._get_subtitles_with_ytdlp(video_id, lang="ru")
        print("\nResult:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("\nError:", str(e))
        import traceback
        traceback.print_exc()
    
    # Test new API
    print("\nTesting YouTube Transcript API (New)...")
    try:
        result = await youtube_service._handle_new_api(video_id, lang="ru")
        print("\nResult:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("\nError:", str(e))
        import traceback
        traceback.print_exc()
    
    # Test old API
    print("\nTesting YouTube Transcript API (Old)...")
    try:
        result = await youtube_service._handle_old_api(video_id, lang="ru")
        print("\nResult:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("\nError:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_transcript_api())

if __name__ == "__main__":
    test_transcript_api()
