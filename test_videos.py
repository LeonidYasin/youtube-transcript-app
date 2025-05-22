import requests
import json
import sys
import io

# Set console output to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_video(video_id, language='en', name="", try_auto_generated=True):
    print(f"\n{'='*50}")
    print(f"Testing video: {name if name else video_id}")
    print(f"URL: https://youtu.be/{video_id}")
    print(f"Language: {language}")
    print("-"*50)
    
    def make_request(use_auto=False):
        params = {'url': video_id}
        if use_auto:
            params['auto_generated'] = 'true'
        else:
    
    if not is_available:
        print("Skipping test - no transcript available")
        return
    
    # Test with auto-generated subtitles if the first attempt fails
    try:
        response = requests.get(
            f"http://localhost:8000/api/transcript/{video_id}",
            params={"language": language, "auto_generated": False}
        )
        
        if response.status_code == 200:
            print(f"Status Code: {response.status_code}")
            print("Raw response (first 200 chars):")
            print("-"*20)
            print(response.text[:200] + ("..." if len(response.text) > 200 else ""))
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            
            # Try with auto-generated subtitles
            print("Trying with auto-generated subtitles...")
            response = requests.get(
                f"http://localhost:8000/api/transcript/{video_id}",
                params={"language": language, "auto_generated": True}
            )
            
            if response.status_code == 200:
                print(f"Status Code (auto-generated): {response.status_code}")
                print("Raw response (first 200 chars):")
                print("-"*20)
                print(response.text[:200] + ("..." if len(response.text) > 200 else ""))
            else:
                print(f"Status Code (auto-generated): {response.status_code}")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Error making request: {str(e)}")

# Test cases with popular Kabbalah-related videos that have available transcripts
test_cases = [
    # Russian Kabbalah videos - using popular Kabbalah Center videos that have transcripts
    {"id": "_z-hEzVfNEs", "lang": "ru", "name": "Введение в Каббалу (Russian)"},
    {"id": "s7G9fU6EPn8", "lang": "ru", "name": "Основные принципы Каббалы (Russian)"},
    
    # Hebrew Kabbalah videos - using popular Kabbalah Center videos
    {"id": "_z-hEzVfNEs", "lang": "he", "name": "הקדמה לחכמת הקבלה (Hebrew)"},
    {"id": "s7G9fU6EPn8", "lang": "he", "name": "עקרונות היסוד של הקבלה (Hebrew)"},
    
    # Test with auto-generated subtitles (English)
    {"id": "_z-hEzVfNEs", "lang": "en", "name": "Kabbalah Introduction (Auto-generated EN)"},
    
    # Test language fallback scenarios
    {"id": "_z-hEzVfNEs", "lang": "fr", "name": "Russian video with French fallback"},
    {"id": "s7G9fU6EPn8", "lang": "es", "name": "Hebrew video with Spanish fallback"}
]

if __name__ == "__main__":
    print("Starting YouTube Transcript API Tests")
    print("="*50)
    
    for test in test_cases:
        test_video(test["id"], test["lang"], test["name"])
    
    print("\nAll tests completed!")
