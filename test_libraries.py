import youtube_transcript_api
import yt_dlp
import json
import sys

# Set console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def test_youtube_transcript_api():
    print("\nTesting youtube-transcript-api...")
    video_id = "tw9USlQh6jw"
    
    try:
        # Get transcript list
        transcript_list = youtube_transcript_api.YouTubeTranscriptApi.list_transcripts(video_id)
        print(f"\nAvailable transcripts for video {video_id}:")
        
        # Print available transcripts
        for transcript in transcript_list:
            print(f"Language: {transcript.language_code} ({transcript.language})")
            print(f"Is auto-generated: {transcript.is_generated}")
            print(f"Available translations: {transcript.translations}")
            print("-" * 50)
        
        # Try to get Russian transcript
        print("\nTrying to get Russian transcript...")
        try:
            transcript = transcript_list.find_manually_created_transcript(['ru'])
            print("\nFound manually created Russian transcript!")
            print(f"Language: {transcript.language_code}")
            print(f"Is auto-generated: {transcript.is_generated}")
            print(f"Available translations: {transcript.translations}")
            
            # Get transcript content
            transcript_content = transcript.fetch()
            print("\nFirst 5 entries:")
            print(json.dumps(transcript_content[:5], indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"\nNo manually created Russian transcript found: {str(e)}")
            
        # Try to get auto-generated transcript
        print("\nTrying to get auto-generated transcript...")
        try:
            transcript = transcript_list.find_generated_transcript(['ru'])
            print("\nFound auto-generated transcript!")
            print(f"Language: {transcript.language_code}")
            print(f"Is auto-generated: {transcript.is_generated}")
            print(f"Available translations: {transcript.translations}")
            
            # Get transcript content
            transcript_content = transcript.fetch()
            print("\nFirst 5 entries:")
            print(json.dumps(transcript_content[:5], indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"\nNo auto-generated transcript found: {str(e)}")
            
    except Exception as e:
        print(f"\nError using youtube-transcript-api: {str(e)}")
        import traceback
        traceback.print_exc()

def test_yt_dlp():
    print("\nTesting yt-dlp...")
    video_id = "tw9USlQh6jw"
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['ru'],
        'quiet': True,
        'no_warnings': True,
        'verbose': True  # Включаем подробный вывод
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nExtracting info for video {video_id}...")
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            
            print("\nAvailable subtitles:")
            print("Manual subtitles:", info.get('subtitles', {}))
            print("Auto-generated subtitles:", info.get('automatic_captions', {}))
            
            # Try to download subtitles
            print("\nTrying to download subtitles...")
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            
    except Exception as e:
        print(f"\nError using yt-dlp: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing libraries directly...")
    test_youtube_transcript_api()
    test_yt_dlp()
