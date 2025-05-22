import requests

def get_transcript(video_url, language='any'):
    """Получает транскрипт видео через API"""
    try:
        response = requests.get(
            'http://localhost:8000/api/transcript',
            params={'url': video_url, 'language': language}
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def print_transcript(result):
    """Выводит результат в удобочитаемом формате"""
    print("\n" + "="*80)
    print(f"URL: {result.get('url', 'N/A')}")
    print(f"Успешно: {'Да' if result.get('success') else 'Нет'}")
    
    if result.get('success'):
        print(f"Язык: {result.get('language', 'Неизвестен')}")
        print(f"Доступные языки: {', '.join(result.get('available_languages', []))}")
        print("\nПервые 500 символов транскрипта:")
        print("-" * 50)
        print(result['transcript'][:500] + ("..." if len(result['transcript']) > 500 else ""))
    else:
        print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        if result.get('available_languages'):
            print(f"Доступные языки: {', '.join(result['available_languages'])}")

if __name__ == "__main__":
    # Популярное видео TED Talk
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    
    print(f"Пытаемся получить транскрипт видео: {video_url}")
    
    # Пробуем получить на русском
    print("\n1. Пробуем получить русский транскрипт:")
    result = get_transcript(video_url, language='ru')
    result['url'] = video_url
    print_transcript(result)
    
    # Если не получилось, пробуем на английском
    if not result.get('success'):
        print("\n2. Пробуем получить английский транскрипт:")
        result = get_transcript(video_url, language='en')
        result['url'] = video_url
        print_transcript(result)
    
    # Если все еще не получилось, пробуем любой доступный
    if not result.get('success'):
        print("\n3. Пробуем получить транскрипт на любом доступном языке:")
        result = get_transcript(video_url, language='any')
        result['url'] = video_url
        print_transcript(result)
