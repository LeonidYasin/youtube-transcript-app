from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json
import requests
from urllib.parse import urlparse

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed = urlparse(url)
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parsed.query.split('v=')[1].split('&')[0]
        elif parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
    elif parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    return None

def get_transcript_with_proxy(video_id, language_code='ru'):
    """Try to get transcript using a proxy"""
    # List of free proxy servers (you may need to update these)
    proxies = [
        {'http': 'http://190.61.88.147:8080', 'https': 'http://190.61.88.147:8080'},
        {'http': 'http://103.155.217.1:41317', 'https': 'http://103.155.217.1:41317'},
        {'http': 'http://103.153.136.186:8080', 'https': 'http://103.153.136.186:8080'},
    ]
    
    for proxy in proxies:
        try:
            print(f"Trying proxy: {proxy}")
            
            # First, get the available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(
                video_id, 
                proxies=proxy
            )
            
            print("\nAvailable transcripts:")
            for transcript in transcript_list:
                print(f"- {transcript.language} ({transcript.language_code}) - Generated: {transcript.is_generated}")
            
            # Try to get the Russian transcript specifically
            transcript = transcript_list.find_transcript([language_code])
            print(f"\nFound {language_code} transcript!")
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Format the transcript as plain text
            formatter = TextFormatter()
            formatted_text = formatter.format_transcript(transcript_data)
            
            # Save to file
            with open(f'transcript_{language_code}_proxy.txt', 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            
            print(f"\nSuccessfully saved transcript to transcript_{language_code}_proxy.txt")
            print("\nPreview of the transcript:")
            print('\n'.join(line['text'] for line in transcript_data[:5]))
            
            return formatted_text
            
        except Exception as e:
            print(f"Error with proxy {proxy}: {str(e)}")
            continue
    
    print("\nAll proxies failed. Trying without proxy as a last resort...")
    
    try:
        # Try without proxy as a last resort
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        
        # Format the transcript as plain text
        formatter = TextFormatter()
        formatted_text = formatter.format_transcript(transcript)
        
        # Save to file
        with open(f'transcript_{language_code}_noproxy.txt', 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"\nSuccessfully saved transcript to transcript_{language_code}_noproxy.txt")
        print("\nPreview of the transcript:")
        print('\n'.join(line['text'] for line in transcript[:5]))
        
        return formatted_text
        
    except Exception as e:
        print(f"\nFailed to get transcript: {str(e)}")
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    video_id = get_video_id(video_url)
    
    if not video_id:
        print("Could not extract video ID from URL")
    else:
        print(f"Getting transcript for video ID: {video_id}")
        transcript = get_transcript_with_proxy(video_id, 'ru')
