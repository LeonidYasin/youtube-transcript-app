import os
import json
import time
from youtubesearchpython import SearchVideos, VideoSortOrder
from app.services.youtube import YouTubeService

def search_channel_videos(channel_name, search_query="", max_results=20):
    """Search for videos from a specific channel."""
    # Combine channel name and search query
    query = f"{search_query} {channel_name}"
    search = SearchVideos(
        query,
        offset=1,
        mode="json",
        max_results=max_results
    )
    
    try:
        results = json.loads(search.result())
        videos = results.get('search_result', [])
        return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

def check_russian_subtitles(video_id):
    """Check if a video has Russian subtitles."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # First try to get Russian subtitles directly
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Check for Russian subtitles
            for transcript in transcript_list:
                if transcript.language_code == 'ru':
                    return True
                
                # Check if Russian is available as a translation
                if transcript.is_translatable:
                    try:
                        transcript.translate('ru')
                        return True
                    except:
                        continue
        except Exception as e:
            print(f"  Error with youtube-transcript-api: {str(e)[:100]}...")
        
        # Try with yt-dlp if available
        try:
            import yt_dlp
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ru'],
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                if info.get('subtitles') and 'ru' in info['subtitles']:
                    return True
                if info.get('automatic_captions') and 'ru' in info['automatic_captions']:
                    return True
        except Exception as e:
            print(f"  Error with yt-dlp: {str(e)[:100]}...")
        
        return False
        
    except Exception as e:
        print(f"  Error checking subtitles: {str(e)[:100]}...")
        return False

def download_russian_subtitles(video_id, output_dir='russian_subtitles'):
    """Download Russian subtitles for a video."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}.txt")
    
    # First try to get Russian subtitles directly
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        try:
            # Try to get Russian transcript directly
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru'])
            text = '\n'.join([item['text'] for item in transcript])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            return True, output_file
            
        except Exception as e:
            print(f"  Couldn't get Russian subtitles directly: {str(e)[:100]}...")
    
    except ImportError:
        print("  youtube-transcript-api not available")
    
    # Fall back to our service
    service = YouTubeService()
    text, error = service.get_subtitles(video_id, lang='ru')
    
    if text:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        return True, output_file
    
    return False, error or "Failed to download subtitles"

def main():
    channel_name = "Ицхак Гинзбург"  # Rav Ginzburg's name in Russian
    search_query = ""  # You can add specific search terms if needed
    
    print(f"Searching for videos from channel: {channel_name}")
    if search_query:
        print(f"With search query: {search_query}")
    
    videos = search_channel_videos(channel_name, search_query, max_results=20)
    
    print(f"\nFound {len(videos)} videos. Checking for Russian subtitles...")
    
    russian_subs_found = 0
    for i, video in enumerate(videos, 1):
        video_id = video.get('id', '')
        video_title = video.get('title', 'Unknown title')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n[{i}/{len(videos)}] Checking: {video_title}")
        print(f"URL: {video_url}")
        
        has_russian = check_russian_subtitles(video_id)
        
        if has_russian:
            print("✅ Found Russian subtitles!")
            success, result = download_russian_subtitles(video_id)
            if success:
                print(f"✅ Downloaded subtitles to: {result}")
                russian_subs_found += 1
            else:
                print(f"❌ Failed to download: {result}")
        else:
            print("❌ No Russian subtitles found")
        
        # Be nice to the servers
        time.sleep(1)
    
    print(f"\nFinished! Found {russian_subs_found} videos with Russian subtitles out of {len(videos)} checked.")

if __name__ == "__main__":
    main()
