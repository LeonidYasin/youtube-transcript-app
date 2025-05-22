import requests
import json
import sys

# Set the console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def test_video(video_url, language):
    print(f"\n{'='*80}")
    print(f"Testing video (language: {language}): {video_url}")
    
    # Make the request
    url = f'http://localhost:8000/api/transcript?url={video_url}&language={language}'
    print(f"Fetching transcript...")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('success') and data.get('transcript'):
            print("✓ Success!")
            transcript = data['transcript']
            print(f"Detected language: {data.get('language', 'unknown')}")
            print(f"Transcript preview (first 200 chars):")
            print("-" * 80)
            print(transcript[:200] + ("..." if len(transcript) > 200 else ""))
            print(f"\nTotal length: {len(transcript)} characters")
        else:
            print("✗ Failed to get transcript:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'response' in locals():
            print(f"Status code: {response.status_code}")
            print("Response content:")
            print(response.text)

# Test with a video that should have Russian subtitles
video_urls = [
    'https://www.youtube.com/watch?v=HluANRwPyNo',  # Simon Sinek: How great leaders inspire action
    'https://www.youtube.com/watch?v=Ks-_Mh1QhMc',  # Tim Urban: Inside the mind of a master procrastinator
    'https://www.youtube.com/watch?v=RcGyVTAoXEU'   # The secret to giving great feedback
]

for video_url in video_urls:
    # Test with Russian
    test_video(video_url, 'ru')
    # Test with English for comparison
    test_video(video_url, 'en')
