import requests
import json
from datetime import datetime
import os

# URL API
BASE_URL = "http://localhost:8000"
TEST_VIDEOS = [
    "xXU4-tiX4Wk",
    "9bZkp7q19f0",
    "tgbNymZ7vqY"
]

def test_video(video_id, language=None):
    print(f"\nTesting video: {video_id}" + (f" with language: {language}" if language else " (default language)"))
    
    # Параметры запроса
    params = {"url": f"https://www.youtube.com/watch?v={video_id}"}
    if language:
        params["language"] = language
    
    # Вызываем API
    response = requests.get(f"{BASE_URL}/api/transcript", params=params)
    
    print(f"Status code: {response.status_code}")
    content_type = response.headers.get('content-type', '')
    print(f"Content type: {content_type}")
    
    # Проверяем тип содержимого
    if 'application/json' in content_type:
        try:
            data = response.json()
            print(f"Response (first 200 chars): {json.dumps(data)[:200]}...")
            print(f"Transcript length: {len(data.get('transcript', ''))} characters")
            print(f"Language used: {data.get('language_used', 'not specified')}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {response.text[:500]}...")
    else:
        # Обработка текстового ответа
        print(f"Text response (first 500 chars): {response.text[:500]}...")
        print(f"Response length: {len(response.text)} characters")

if __name__ == "__main__":
    print("Testing API with different language scenarios...")
    
    # Test each video with different language settings
    for video_id in TEST_VIDEOS:
        # Test with default language (should be 'ru' as per settings)
        test_video(video_id)
        
        # Test with explicit Russian language
        test_video(video_id, language='ru')
        
        # Test with English language
        test_video(video_id, language='en')
        
        print("\n" + "="*80 + "\n")
