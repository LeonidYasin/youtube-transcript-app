import sys
from transcript_service import get_transcript

def print_result(result):
    """Выводит результат в удобочитаемом формате"""
    print("\n" + "="*80)
    print(f"URL: {result.get('url', 'N/A')}")
    print(f"Успешно: {'Да' if result['success'] else 'Нет'}")
    
    if result['success']:
        print(f"Язык: {result.get('language', 'Неизвестен')}")
        print(f"Доступные языки: {', '.join(result.get('available_languages', []))}")
        print("\nПервые 200 символов транскрипта:")
        print("-" * 50)
        print(result['transcript'][:200] + ("..." if len(result['transcript']) > 200 else ""))
    else:
        print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        if result.get('available_languages'):
            print(f"Доступные языки: {', '.join(result['available_languages'])}")

def test_video(url, language='any'):
    """Тестирует получение транскрипта для указанного URL"""
    print(f"\nТестирование видео: {url}")
    print(f"Запрошенный язык: {language if language != 'any' else 'Любой доступный'}")
    
    try:
        result = get_transcript(url, language)
        result['url'] = url
        print_result(result)
        return result
    except Exception as e:
        print(f"Ошибка при тестировании {url}: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }

if __name__ == "__main__":
    # Тестовые URL
    test_urls = [
        # Русские видео
        ("https://www.youtube.com/watch?v=Ks-_Mh1QhMc", "ru"),  # Tim Urban: Inside the mind of a master procrastinator
        ("https://www.youtube.com/watch?v=5MgBikgcWnY", "ru"),  # Andrew Ng: What's Next in Deep Learning
        
        # Английские видео
        ("https://www.youtube.com/watch?v=HluANRwPyNo", "en"),  # Simon Sinek: How great leaders inspire action
        ("https://www.youtube.com/watch?v=RcGyVTAoXEU", "en"),  # The secret to giving great feedback
        
        # Видео с разными языками
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "any"),  # Rick Astley - Never Gonna Give You Up
        ("https://www.youtube.com/watch?v=JGwWNGJdvx8", "any"),  # Ed Sheeran - Shape of You
    ]
    
    print("Начинаем тестирование сервиса транскрипции...")
    
    # Запускаем тесты
    results = []
    for url, lang in test_urls:
        result = test_video(url, lang)
        results.append(result)
    
    # Выводим статистику
    success_count = sum(1 for r in results if r.get('success'))
    print("\n" + "="*50)
    print(f"Тестирование завершено! Успешно: {success_count} из {len(results)}")
    
    # Показываем ошибки, если есть
    failed = [r for r in results if not r.get('success')]
    if failed:
        print("\nНе удалось получить транскрипт для:")
        for i, fail in enumerate(failed, 1):
            print(f"{i}. {fail['url']}")
            print(f"   Ошибка: {fail.get('error', 'Неизвестная ошибка')}")
            if fail.get('available_languages'):
                print(f"   Доступные языки: {', '.join(fail['available_languages'])}")
