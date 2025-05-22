import requests
import json

# Base URL of the API
BASE_URL = "http://localhost:8000"

def test_video(video_id, language=None):
    """Test the API with a specific video ID and optional language"""
    print("\n" + "="*80)
    print(f"Testing video: {video_id}" + (f" with language: {language}" if language else " (default - native language)"))
    print("-" * 80)
    
    # Prepare parameters
    params = {"url": f"https://www.youtube.com/watch?v={video_id}"}
    if language:
        params["language"] = language
    
    try:
        # Make the request
        response = requests.get(f"{BASE_URL}/api/transcript", params=params)
        
        # Print results
        print(f"Status code: {response.status_code}")
        
        # Print response headers that show language information
        if response.status_code == 200:
            if 'X-Subtitles-Language' in response.headers:
                lang = response.headers['X-Subtitles-Language']
                print(f"[SUCCESS] Detected language: {lang}")
                if 'X-Subtitles-Auto-Generated' in response.headers:
                    print("   - Using auto-generated subtitles")
                else:
                    print("   - Using manual subtitles")
            
            # Print the first 200 characters of the response
            text_response = response.text
            print(f"\nResponse length: {len(text_response)} characters")
            
            try:
                # Try to print with default encoding first
                preview = text_response[:200]
                if len(text_response) > 200:
                    preview += "..."
                print("\nPreview:")
                print("-" * 40)
                print(preview)
                print("-" * 40)
            except UnicodeEncodeError:
                # If there's an encoding error, replace or ignore problematic characters
                print("\nPreview (with encoding issues):")
                print("-" * 40)
                print(text_response[:200].encode('ascii', 'replace').decode('ascii') + 
                      ('...' if len(text_response) > 200 else ''))
                print("-" * 40)
        else:
            print(f"[ERROR] {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")

# Test with different videos from various languages
TEST_VIDEOS = [
    {"id": "dQw4w9WgXcQ", "lang": None, "desc": "English song (Rick Astley - Never Gonna Give You Up)"},
    {"id": "9bZkp7q19f0", "lang": None, "desc": "Korean song (Gangnam Style)"},
    {"id": "JGwWNGJdvx8", "lang": None, "desc": "English song (Ed Sheeran - Shape of You)"},
    {"id": "9bW4_chtAHE", "lang": None, "desc": "Russian video (Владимир Высоцкий - Кони привередливые)"},
    {"id": "RgKAFK5djSk", "lang": None, "desc": "English song with multiple subtitles (See You Again)"},
    {"id": "JGwWNGJdvx8", "lang": "ru", "desc": "English song with Russian subtitles request"},
    {"id": "JGwWNGJdvx8", "lang": "es", "desc": "English song with Spanish subtitles request"},
    {"id": "9bZkp7q19f0", "lang": "en", "desc": "Korean song with explicit English subtitles request"}
]

def print_header(text):
    print("\n" + "="*80)
    print(f" {text} ")
    print("="*80 + "\n")

if __name__ == "__main__":
    print_header("Testing YouTube Transcript API with Native Language Detection")
    
    for test_case in TEST_VIDEOS:
        video_id = test_case["id"]
        lang = test_case.get("lang")
        desc = test_case.get("desc", "")
        
        print_header(f"Video: {desc}")
        print(f"Video ID: {video_id}")
        if lang:
            print(f"Requested language: {lang}")
        else:
            print("No language specified (will use native)")
        
        test_video(video_id, lang)
        
        # Only test with English if not already testing a specific language
        if not lang:
            print("\n" + "-"*40 + "\n")
            print("Testing the same video with explicit English request:")
            test_video(video_id, "en")
        
        print("\n" + "="*80 + "\n")
