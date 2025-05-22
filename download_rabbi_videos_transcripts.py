import os
import json
import time
import sys
from datetime import datetime
import requests

# Configure console for UTF-8 output
if sys.platform == 'win32':
    import io
    import sys
    import codecs
    
    # Set stdout and stderr to use UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Set console output code page to UTF-8
    os.system('chcp 65001 > nul')
    
    # Set environment variable to force UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configuration
OUTPUT_DIR = "rabbi_ginsburgh_transcripts"
CHANNEL_ID = "UCKadAPtEb8TTfPrQY3qwKpQ"  # Rabbi Ginsburgh's channel ID
MAX_VIDEOS = 10

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_print(text):
    """Safely print text that might contain non-ASCII characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # If we can't print the text, print a simplified version
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def get_channel_videos():
    """Fetch the latest videos from the channel"""
    url = f"http://127.0.0.1:8000/api/channel-search/{CHANNEL_ID}/videos"
    params = {"max_results": MAX_VIDEOS}
    
    try:
        safe_print(f"\nFetching {MAX_VIDEOS} most recent videos from the channel...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'videos' in data:
            safe_print(f"Successfully retrieved {len(data['videos'])} videos.")
        else:
            safe_print("No videos found in the response.")
            
        return data
    except Exception as e:
        safe_print(f"Error fetching channel videos: {e}")
        if 'response' in locals():
            safe_print(f"Response status code: {response.status_code}")
            safe_print(f"Response content: {response.text[:500]}")
        return None

def parse_vtt_to_segments(vtt_content):
    """Convert VTT content to segments format"""
    segments = []
    lines = vtt_content.split('\n')
    
    # Skip the WEBVTT header if present
    start_idx = 0
    if lines and lines[0].strip().upper() == 'WEBVTT':
        start_idx = 1
    
    current_segment = None
    
    for line in lines[start_idx:]:
        line = line.strip()
        if '-->' in line:  # Timestamp line
            if current_segment:
                segments.append(current_segment)
            times = line.split('-->')
            if len(times) >= 2:
                start_time = times[0].strip()
                current_segment = {
                    'start': start_time,
                    'text': ''
                }
        elif line and current_segment and not line.isdigit():
            # Add text to current segment
            if current_segment['text']:
                current_segment['text'] += ' ' + line
            else:
                current_segment['text'] = line
    
    # Add the last segment
    if current_segment and current_segment['text']:
        segments.append(current_segment)
    
    return segments

def get_video_transcript(video_id, video_title):
    """Fetch transcript for a single video"""
    url = "http://127.0.0.1:8000/api/transcript/api/transcript"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    params = {
        "url": video_url,
        "language": "ru"  # Requesting Russian transcript
    }
    
    try:
        safe_print(f"\nFetching transcript for video: {video_title}")
        safe_print(f"Video ID: {video_id}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Check if response is VTT format
        content_type = response.headers.get('content-type', '')
        if 'text/vtt' in content_type or response.text.strip().startswith('WEBVTT'):
            safe_print("Received VTT format, converting to segments...")
            segments = parse_vtt_to_segments(response.text)
            transcript_data = {
                'status': 'success',
                'format': 'vtt',
                'segments': segments,
                'segment_count': len(segments)
            }
        else:
            # Try to parse as JSON
            try:
                transcript_data = response.json()
                transcript_data['format'] = 'json'
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                safe_print("Response is not JSON, treating as plain text...")
                transcript_data = {
                    'status': 'success',
                    'format': 'text',
                    'content': response.text,
                    'segment_count': 1
                }
        
        if 'segments' in transcript_data and transcript_data['segments']:
            safe_print(f"Successfully retrieved transcript with {len(transcript_data['segments'])} segments.")
        elif 'content' in transcript_data:
            safe_print(f"Retrieved transcript content (length: {len(transcript_data['content'])} chars)")
        else:
            safe_print("No transcript data found in the response.")
            
        return transcript_data
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {e}"
        safe_print(error_msg)
        if 'response' in locals():
            safe_print(f"Status code: {response.status_code}")
            safe_print(f"Response: {response.text[:500]}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        safe_print(error_msg)
        return {'status': 'error', 'message': str(e)}

def save_transcript(video_info, transcript_data):
    """Save transcript to a JSON file"""
    if not transcript_data:
        safe_print("No transcript data provided")
        return None
        
    if not isinstance(transcript_data, dict):
        safe_print(f"Unexpected transcript data type: {type(transcript_data)}")
        return None
        
    if 'segments' not in transcript_data and 'content' not in transcript_data:
        safe_print(f"No transcript segments or content found in the response for video: {video_info.get('title')}")
        safe_print(f"Available keys: {list(transcript_data.keys())}")
        return None
    
    try:
        # Create a safe filename using only ASCII characters
        safe_title = "".join(c if c.isascii() and (c.isalnum() or c in ' _-') else '_' for c in video_info['title'])
        safe_title = safe_title.strip('_')  # Remove any leading/trailing underscores
        safe_title = safe_title[:50] or f"video_{video_info['video_id']}"  # Limit filename length
        
        # Add video ID and timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{video_info['video_id']}_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Prepare data to save
        save_data = {
            "video_info": video_info,
            "transcript": transcript_data,
            "retrieved_at": datetime.now().isoformat()
        }
        
        # Save to file with proper encoding
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        safe_print(f"Successfully saved transcript to: {filepath}")
        return filepath
        
    except Exception as e:
        safe_print(f"Error saving transcript: {e}")
        safe_print(f"File path: {filepath}")
        return None
    
    # Prepare data to save
    save_data = {
        "video_info": video_info,
        "transcript": transcript_data,
        "retrieved_at": datetime.now().isoformat()
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"Saved transcript to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving transcript to {filepath}: {e}")
        return None

def main():
    print(f"Fetching {MAX_VIDEOS} most recent videos from Rabbi Ginsburgh's channel...")
    channel_data = get_channel_videos()
    
    if not channel_data or 'videos' not in channel_data:
        print("Failed to fetch channel videos. Please check the server and try again.")
        return
    
    print(f"\nFound {len(channel_data['videos'])} videos. Starting transcript download...")
    print("-" * 80)
    
    for video in channel_data['videos']:
        video_id = video['video_id']
        video_title = video['title']
        
        # Get transcript
        transcript = get_video_transcript(video_id, video_title)
        
        if transcript:
            # Save transcript to file
            save_transcript(video, transcript)
            print("-" * 80)
        
        # Add a small delay between requests to be gentle on the server
        time.sleep(1)
    
    print("\nTranscript download complete!")

if __name__ == "__main__":
    main()
