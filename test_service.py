import requests
import json
import time

def test_endpoint(url, params=None, method='GET', data=None):
    """Универсальная функция для тестирования эндпоинтов"""
    try:
        start_time = time.time()
        
        if method.upper() == 'GET':
            response = requests.get(url, params=params, timeout=10)
        else:
            response = requests.post(url, json=data, params=params, timeout=10)
            
        response_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"Testing: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.2f} seconds")
        
        try:
            json_response = response.json()
            print("Response JSON:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
            
            # Проверяем структуру ответа
            if 'success' in json_response:
                if json_response['success']:
                    print("[SUCCESS] Success: True")
                    # Проверяем наличие обязательных полей
                    if 'transcript' in json_response:
                        transcript = json_response['transcript']
                        print(f"Transcript length: {len(transcript)} characters")
                        print("First 200 chars:", transcript[:200].replace('\n', '\\n'))
                        
                    if 'available_languages' in json_response:
                        langs = json_response['available_languages']
                        print(f"Available languages: {', '.join(langs) if langs else 'None'}")
                else:
                    print(f"[ERROR] Error: {json_response.get('error', 'Unknown error')}")
            
        except json.JSONDecodeError:
            print("Response is not JSON:")
            print(response.text[:500])
            
        return response
        
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")
        return None

def test_transcript_api():
    base_url = "http://localhost:8000/api/"
    video_id = "qp0HIF3SfI4"  # Simon Sinek TED Talk
    
    # Тест 1: Получение списка языков
    print("\n" + "="*50 + " TEST 1: GET AVAILABLE LANGUAGES " + "="*50)
    test_endpoint(f"{base_url}languages/{video_id}")
    
    # Тест 2: Получение транскрипта на русском
    print("\n" + "="*50 + " TEST 2: GET RUSSIAN TRANSCRIPT " + "="*50)
    test_endpoint(
        f"{base_url}transcript",
        params={"url": f"https://www.youtube.com/watch?v={video_id}", "language": "ru"}
    )
    
    # Тест 3: Получение транскрипта на английском
    print("\n" + "="*50 + " TEST 3: GET ENGLISH TRANSCRIPT " + "="*50)
    test_endpoint(
        f"{base_url}transcript",
        params={"url": f"https://www.youtube.com/watch?v={video_id}", "language": "en"}
    )
    
    # Тест 4: Получение транскрипта без указания языка
    print("\n" + "="*50 + " TEST 4: GET TRANSCRIPT WITHOUT LANGUAGE " + "="*50)
    test_endpoint(
        f"{base_url}transcript",
        params={"url": f"https://www.youtube.com/watch?v={video_id}"}
    )
    
    # Тест 5: Неверный URL видео
    print("\n" + "="*50 + " TEST 5: INVALID VIDEO URL " + "="*50)
    test_endpoint(
        f"{base_url}transcript",
        params={"url": "https://www.youtube.com/watch?v=INVALID_VIDEO_ID"}
    )

if __name__ == "__main__":
    print("Starting YouTube Transcript API Tests...")
    test_transcript_api()
    print("\nAll tests completed!")
