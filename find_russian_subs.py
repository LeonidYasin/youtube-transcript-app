import os
import json
import time
from googleapiclient.discovery import build
from app.services.youtube import YouTubeService

# You'll need to get a YouTube Data API key from Google Cloud Console
# Set it as an environment variable: YOUTUBE_API_KEY
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Rav Ginzburg's channel ID (you can find this in the channel URL)
CHANNEL_ID = 'UCqG3nGvmS5XoI8uD0i0HZwQ'  # This is an example, replace with actual channel ID

def get_channel_videos(max_results=50):
    """Fetch videos from the channel."""
    youtube = build(
        YOUTUBE_API_SERVICE_NAME, 
        YOUTUBE_API_VERSION, 
        developerKey=YOUTUBE_API_KEY
    )
    
    # Get uploads playlist ID
    channels_response = youtube.channels().list(
        id=CHANNEL_ID,
        part='contentDetails'
    ).execute()
    
    uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get videos from the uploads playlist
    videos = []
    next_page_token = None
    
    while len(videos) < max_results:
        playlist_items_response = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet',
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page_token
        ).execute()
        
        for item in playlist_items_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            videos.append({
                'id': video_id,
                'title': video_title,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            })
        
        next_page_token = playlist_items_response.get('nextPageToken')
        if not next_page_token or len(videos) >= max_results:
            break
    
    return videos

def check_russian_subtitles(video_id):
    """Check if a video has Russian subtitles."""
    service = YouTubeService()
    
    # First check with youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
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
        print(f"Error checking subtitles for {video_id}: {e}")
    
    # If no luck, try with yt-dlp
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
        print(f"Error with yt-dlp for {video_id}: {e}")
    
    return False

def download_russian_subtitles(video_id, output_dir='russian_subtitles'):
    """Download Russian subtitles for a video."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{video_id}.txt")
    
    service = YouTubeService()
    text, error = service.get_subtitles(video_id, lang='ru')
    
    if text:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        return True, output_file
    
    return False, error

def main():
    if not YOUTUBE_API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        print("Please get an API key from Google Cloud Console and set it as YOUTUBE_API_KEY")
        return
    
    print(f"Fetching videos from channel {CHANNEL_ID}...")
    videos = get_channel_videos(max_results=20)  # Check first 20 videos
    
    print(f"\nFound {len(videos)} videos. Checking for Russian subtitles...")
    
    russian_subs_found = 0
    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Checking: {video['title']}")
        print(f"URL: {video['url']}")
        
        has_russian = check_russian_subtitles(video['id'])
        
        if has_russian:
            print("✅ Found Russian subtitles!")
            success, result = download_russian_subtitles(video['id'])
            if success:
                print(f"✅ Downloaded subtitles to: {result}")
                russian_subs_found += 1
            else:
                print(f"❌ Failed to download: {result}")
        else:
            print("❌ No Russian subtitles found")
        
        # Be nice to the API
        time.sleep(1)
    
    print(f"\nFinished! Found {russian_subs_found} videos with Russian subtitles out of {len(videos)} checked.")

if __name__ == "__main__":
    main()
