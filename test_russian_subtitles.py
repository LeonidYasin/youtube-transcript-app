import logging
from app.services.youtube import YouTubeService

# Set up logging to see the process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_russian_subtitles(video_id):
    print("\n=== Testing Russian Subtitles ===")
    print(f"Video ID: {video_id}")
    
    service = YouTubeService()
    
    # Try to get Russian subtitles
    print("\nAttempting to get Russian subtitles...")
    text, error = service.get_subtitles(video_id, lang='ru')
    
    if text:
        print("\n=== Russian Subtitles Found ===")
        print(f"First 500 characters: {text[:500]}...")
        print(f"\nTotal length: {len(text)} characters")
    else:
        print("\n=== Error ===")
        print(f"Could not get Russian subtitles: {error}")
        
        # Check what languages are available
        print("\nChecking available languages...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            print("\nAvailable manual transcripts:")
            for transcript in transcript_list:
                print(f"- {transcript.language} ({transcript.language_code}): "
                      f"{'auto-generated' if transcript.is_generated else 'manual'}")
            
            print("\nAvailable generated transcripts:")
            for transcript in transcript_list:
                if transcript.is_translatable:
                    print(f"- {transcript.language} ({transcript.language_code}) can be translated")
        except Exception as e:
            print(f"Error checking available languages: {e}")

if __name__ == "__main__":
    test_russian_subtitles("xXU4-tiX4Wk")  # Rav Ginzburg video
