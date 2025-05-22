import requests

def test_transcript_api():
    url = "http://localhost:8000/api/transcript"
    params = {
        "url": "https://www.youtube.com/watch?v=qp0HIF3SfI4",
        "language": "en"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        
        data = response.json()
        
        if data.get("success"):
            print("Транскрипт успешно получен!")
            print(f"Язык: {data.get('language')}")
            print(f"Доступные языки: {', '.join(data.get('available_languages', []))}")
            print("\nПервые 500 символов транскрипта:")
            print("-" * 50)
            print(data['transcript'][:500] + ("..." if len(data['transcript']) > 500 else ""))
        else:
            print(f"Ошибка: {data.get('error')}")
            if data.get('available_languages'):
                print(f"Доступные языки: {', '.join(data['available_languages'])}")
                
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
    except ValueError as e:
        print(f"Ошибка при обработке ответа: {e}")
        print(f"Ответ сервера: {response.text[:500]}")

if __name__ == "__main__":
    test_transcript_api()
