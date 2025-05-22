import requests
import json

def get_full_transcript(video_url, language='ru'):
    """
    Получает полный транскрипт видео на указанном языке
    
    Аргументы:
        video_url (str): URL YouTube видео
        language (str): Код языка (по умолчанию 'ru' для русского)
    """
    base_url = "http://localhost:8000/api/transcript"
    params = {
        "url": video_url,
        "language": language
    }
    
    try:
        print(f"Запрос транскрипта для видео: {video_url}")
        print(f"Язык: {language}")
        print("-" * 50)
        
        # Отправляем запрос к нашему API
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success"):
            # Сохраняем полный транскрипт в файл
            output_file = f"transcript_{data['video_id']}_{language}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data['transcript'])
            
            print(f"✅ Транскрипт успешно сохранен в файл: {output_file}")
            print(f"Язык: {data.get('language')}")
            print(f"Доступные языки: {', '.join(data.get('available_languages', []))}")
            print(f"\nПервые 500 символов:\n" + "-" * 50)
            print(data['transcript'][:500] + ("..." if len(data['transcript']) > 500 else ""))
            print("\n...")
            print("-" * 50)
            print(f"Всего символов: {len(data['transcript'])}")
            
            return output_file
        else:
            print(f"❌ Ошибка: {data.get('error')}")
            if data.get('available_languages'):
                print(f"Доступные языки: {', '.join(data['available_languages'])}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None

if __name__ == "__main__":
    # TED Talk: Simon Sinek - How great leaders inspire action
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    
    # Пробуем получить русский транскрипт
    result = get_full_transcript(video_url, language='ru')
    
    if not result:
        print("\nПопытка получить английский транскрипт...")
        get_full_transcript(video_url, language='en')
