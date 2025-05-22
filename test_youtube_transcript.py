"""
Test script for YouTube transcript functionality with proper encoding handling.
"""
import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id: str, language: str = 'iw'):
    """Get transcript for a YouTube video with the given language."""
    try:
        # First try to get the transcript with the specified language
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=[language],
            preserve_formatting=True
        )
        return transcript, None
    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_youtube_transcript.py <video_id> [language]")
        return
        
    video_id = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'iw'
    
    print(f"Fetching transcript for video: {video_id} (language: {language})")
    
    # Get the transcript
    transcript, error = get_transcript(video_id, language)
    
    if error:
        print(f"Error: {error}")
    else:
        # Save to file with proper encoding
        output_file = f"transcript_{video_id}_{language}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        print(f"Transcript saved to {output_file}")
        
        # Print first few lines
        print("\nFirst few lines of the transcript:")
        for i, entry in enumerate(transcript[:5]):
            print(f"{i+1}. {entry['text']}")

if __name__ == "__main__":
    main()
