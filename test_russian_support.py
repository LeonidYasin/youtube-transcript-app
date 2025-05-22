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
            print(f"Detected language: {data.get('language', 'unknown')}")
            if data.get('is_translation'):
                print(f"Note: This is a translation from {data.get('original_language', 'unknown')}")
            if 'available_languages' in data:
                print(f"Available languages: {', '.join(data['available_languages'])}")
                
            transcript = data['transcript']
            print(f"\nTranscript preview (first 200 chars):")
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
    'https://www.youtube.com/watch?v=RcGyVTAoXEU',  # The secret to giving great feedback
    'https://www.youtube.com/watch?v=5MgBikgcWnY'   # Andrew Ng: What's Next in Deep Learning
]

for video_url in video_urls:
    # Test with Russian first
    test_video(video_url, 'ru')
    # Then test with English for comparison
    test_video(video_url, 'en')
