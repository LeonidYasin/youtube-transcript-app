import logging
from app.services.youtube import YouTubeService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Test the service
def test_service():
    print("\n=== Testing YouTube Service ===")
    service = YouTubeService()
    
    video_id = "xXU4-tiX4Wk"  # Rav Ginzburg video
    lang = "iw"  # Hebrew
    
    print(f"\nGetting transcript for video {video_id} in {lang}...")
    text, error = service.get_subtitles(video_id, lang)
    
    print("=== Results ===")
    if text:
        print(f"Success! Retrieved {len(text)} characters of text.")
        try:
            print(f"First 200 chars: {text[:200]}...")
        except UnicodeEncodeError:
            print("First 200 chars (hex):", ' '.join(f'{ord(c):04x}' for c in text[:200]))
    if error:
        print(f"Error: {error}")

if __name__ == "__main__":
    test_service()
