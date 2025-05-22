import os
import json
import requests
from datetime import datetime

# Configuration
OUTPUT_DIR = "rabbi_ginsburgh_transcripts"
CHANNEL_ID = "UCKadAPtEb8TTfPrQY3qwKpQ"
MAX_VIDEOS = 10

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_print(text):
    """Safely print text that might contain non-ASCII characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def get_channel_videos():
    """Fetch the latest videos from the channel"""
    url = f"http://127.0.0.1:8000/api/channel-search/{CHANNEL_ID}/videos"
    params = {"max_results": MAX_VIDEOS}
    
    try:
        print(f"\nFetching {MAX_VIDEOS} most recent videos...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'videos' in data and data['videos']:
            print(f"Found {len(data['videos'])} videos.")
            return data['videos']
        else:
            print("No videos found in the response.")
            return []
            
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        if 'response' in locals():
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        return []

def get_video_transcript(video_id, video_title):
    """Fetch transcript for a single video"""
    url = "http://127.0.0.1:8000/api/transcript/api/transcript"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        print(f"\nFetching transcript for: {video_title}")
        print(f"Video ID: {video_id}")
        
        response = requests.get(url, params={"url": video_url, "language": "ru"}, timeout=30)
        response.raise_for_status()
        
        # Save raw response for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_filename = os.path.join(OUTPUT_DIR, f"raw_{video_id}_{timestamp}.txt")
        with open(raw_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved raw response to: {raw_filename}")
        
        # Try to parse as JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {"status": "success", "format": "text", "content": response.text}
            
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        if 'response' in locals():
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        return {"status": "error", "message": str(e)}

def save_transcript(video_info, transcript_data):
    """Save transcript to a JSON file"""
    if not transcript_data:
        print("No transcript data to save")
        return None
    
    try:
        # Create a safe filename
        safe_title = "".join(c if c.isalnum() or c in ' _-' else '_' for c in video_info.get('title', ''))
        safe_title = safe_title[:50] or f"video_{video_info.get('video_id', 'unknown')}"
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{video_info.get('video_id', '')}_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Prepare data to save
        data_to_save = {
            "video_info": video_info,
            "transcript": transcript_data,
            "retrieved_at": datetime.now().isoformat()
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
        print(f"Saved transcript to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error saving transcript: {e}")
        return None

def main():
    print("Starting transcript download process...")
    
    # Get list of videos
    videos = get_channel_videos()
    if not videos:
        print("No videos found. Exiting.")
        return
    
    print("\nStarting transcript downloads...")
    print("-" * 50)
    
    for video in videos:
        # Get transcript
        transcript = get_video_transcript(video['video_id'], video.get('title', 'No title'))
        
        # Save transcript
        if transcript:
            save_transcript(video, transcript)
        
        print("-" * 50)
    
    print("\nTranscript download process completed!")

if __name__ == "__main__":
    main()
