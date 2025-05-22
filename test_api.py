import requests

def test_transcript_api():
    # URL API
    api_url = "http://localhost:8000/api/transcript"
    
    # Тестовые данные
    test_cases = [
        {
            "url": "https://www.youtube.com/watch?v=7CmkwhWqUzE",
            "language": "ru",
            "description": "Видео с русскими субтитрами"
        },
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "language": "en",
            "description": "Видео с английскими субтитрами"
        },
        {
            "url": "https://youtu.be/7CmkwhWqUzE",
            "language": "ru",
            "description": "Короткая ссылка youtu.be"
        },
        {
            "url": "https://www.youtube.com/watch?v=invalid_video_id",
            "language": "ru",
            "description": "Неверный ID видео"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"Тест: {test['description']}")
        print(f"URL: {test['url']}")
        print(f"Язык: {test['language']}")
        
        try:
            # Отправляем запрос к API
            response = requests.get(
                api_url,
                params={
                    "url": test['url'],
                    "language": test['language']
                }
            )
            
            # Выводим результаты
            print(f"\nСтатус код: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                print("\nТранскрипт успешно получен!")
                print(f"ID видео: {data['video_id']}")
                print(f"\nПервые 200 символов транскрипта:")
                print(data['transcript'][:200] + "..." if len(data['transcript']) > 200 else data['transcript'])
            else:
                print("\nОшибка при получении транскрипта:")
                print(f"Ошибка: {data.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            print(f"\nПроизошла ошибка при выполнении запроса: {str(e)}")

if __name__ == "__main__":
    test_transcript_api()
