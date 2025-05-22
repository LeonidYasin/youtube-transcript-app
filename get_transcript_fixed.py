from youtube_transcript_api import YouTubeTranscriptApi
import json

def get_transcript(video_id, language='ru'):
    """
    Получает транскрипт видео на указанном языке
    
    Аргументы:
        video_id (str): ID YouTube видео
        language (str): Код языка (по умолчанию 'ru')
    """
    try:
        print(f"Попытка получить транскрипт для видео {video_id} на языке {language}...")
        
        # Пытаемся получить транскрипт на указанном языке
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=[language, 'en']  # Сначала пробуем русский, потом английский
        )
        
        # Форматируем результат в текст
        text = '\n'.join([t['text'] for t in transcript])
        
        # Получаем информацию о доступных языках
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = []
        
        for t in transcript_list:
            available_languages.append({
                'code': t.language_code,
                'name': t.language,
                'is_generated': t.is_generated,
                'is_translatable': t.is_translatable
            })
        
        # Сохраняем результат в файл
        output_file = f"transcript_{video_id}_{language}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Транскрипт успешно сохранен в файл: {output_file}")
        print(f"Доступные языки: {', '.join([f'{lang['name']} ({lang['code']})' for lang in available_languages])}")
        
        # Выводим первые 500 символов для предпросмотра
        print("\nПервые 500 символов транскрипта:")
        print("-" * 60)
        print(text[:500] + ("..." if len(text) > 500 else ""))
        
        return {
            'success': True,
            'video_id': video_id,
            'language': language,
            'available_languages': [lang['code'] for lang in available_languages],
            'transcript': text
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"Ошибка: {error_msg}")
        
        # Пытаемся получить список доступных языков для лучшего сообщения об ошибке
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = [t.language_code for t in transcript_list]
            print(f"Доступные языки: {', '.join(available_languages)}")
            
            return {
                'success': False,
                'error': f"Транскрипт на языке '{language}' не найден. Доступные языки: {', '.join(available_languages)}",
                'video_id': video_id,
                'available_languages': available_languages
            }
        except Exception as e2:
            return {
                'success': False,
                'error': f"Не удалось получить транскрипт: {error_msg}",
                'video_id': video_id,
                'available_languages': []
            }

if __name__ == "__main__":
    # TED Talk: Simon Sinek - How great leaders inspire action
    video_id = "qp0HIF3SfI4"
    
    # Пробуем получить русский транскрипт
    result = get_transcript(video_id, language='ru')
    
    # Если русский не найден, пробуем английский
    if not result.get('success'):
        print("\nПопытка получить английский транскрипт...")
        get_transcript(video_id, language='en')
