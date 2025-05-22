import os
import time
import sys
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi

# Set console to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def search_videos(query, max_results=20):
    """Search for videos using youtube-search-python."""
    try:
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        return results
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

def has_russian_subtitles(video_id):
    """Check if a video has Russian subtitles."""
    try:
        # First try to get Russian subtitles directly
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
        return False
    except Exception as e:
        print(f"  Error checking subtitles for {video_id}: {str(e)[:100]}...")
        return False

def download_subtitles(video_id, output_dir='russian_subtitles'):
    """Download Russian subtitles for a video."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}.txt")
    
    try:
        # Try to get Russian transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru'])
        text = '\n'.join([item['text'] for item in transcript])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        return True, output_file
    except Exception as e:
        return False, str(e)

def main():
    search_query = "Ицхак Гинзбург"  # Rav Ginzburg's name in Russian
    
    print(f"Searching for videos: {search_query}")
    videos = search_videos(search_query, max_results=20)
    
    if not videos:
        print("No videos found.")
        return
        
    print(f"\nFound {len(videos)} videos. Checking for Russian subtitles...")
    
    russian_subs_found = 0
    for i, video in enumerate(videos, 1):
        video_id = video.get('id', '')
        video_title = video.get('title', 'Unknown title')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n[{i}/{len(videos)}] Checking: {video_title}")
        print(f"URL: {video_url}")
        
        has_russian = has_russian_subtitles(video_id)
        
        if has_russian:
            print("[FOUND] Found Russian subtitles!")
            success, result = download_subtitles(video_id)
            if success:
                print(f"[SUCCESS] Downloaded subtitles to: {result}")
                russian_subs_found += 1
            else:
                print(f"[ERROR] Failed to download: {result}")
        else:
            print("[INFO] No Russian subtitles found")
        
        # Be nice to the servers
        time.sleep(1)
    
    print(f"\nFinished! Found {russian_subs_found} videos with Russian subtitles out of {len(videos)} checked.")

if __name__ == "__main__":
    main()
