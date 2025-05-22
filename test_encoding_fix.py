from youtube_transcript_api import YouTubeTranscriptApi
import json

def print_raw_data(transcript):
    """Печатает сырые данные транскрипции"""
    if not transcript:
        print("Транскрипция не найдена")
        return
    
    print("\n=== Сырые данные (первые 5 сегментов) ===")
    for i, segment in enumerate(transcript[:5]):
        print(f"\n--- Сегмент {i+1} ---")
        print(f"Тип: {type(segment)}")
        print(f"Ключи: {list(segment.keys()) if isinstance(segment, dict) else 'N/A'}")
        
        if isinstance(segment, dict):
            print("Содержимое:")
            for key, value in segment.items():
                if isinstance(value, str):
                    print(f"  {key}: {value!r}")
                else:
                    print(f"  {key}: {value}")
                    
def test_decoding(transcript):
    """Тестирует различные способы декодирования"""
    if not transcript or not isinstance(transcript[0], dict) or 'text' not in transcript[0]:
        print("Невозможно протестировать декодирование: неверный формат данных")
        return
    
    text = transcript[0]['text']
    print("\n=== Тестирование декодирования ===")
    print(f"Исходный текст: {text!r}")
    
    # Пробуем разные кодировки
    encodings = ['utf-8', 'cp1251', 'cp1252', 'latin1', 'koi8-r', 'iso-8859-1', 'utf-16', 'utf-16-le', 'utf-16-be']
    
    for enc in encodings:
        try:
            # Пробуем как есть
            try:
                decoded = text.encode(enc).decode('utf-8')
                print(f"\n{enc} -> utf-8: {decoded!r}")
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                print(f"\n{enc} -> utf-8: Ошибка - {str(e)}")
                
            # Пробуем с двойным преобразованием
            try:
                double_decoded = text.encode('latin1').decode(enc).encode('utf-8').decode('utf-8')
                print(f"latin1 -> {enc} -> utf-8: {double_decoded!r}")
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                pass
                
        except Exception as e:
            print(f"Ошибка при тестировании кодировки {enc}: {str(e)}")

def main():
    video_id = "qp0HIF3SfI4"
    language = "ru"
    
    try:
        print(f"Получение транскрипции для видео {video_id}...")
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[language],
            preserve_formatting=True
        )
        
        if not transcript:
            print("Транскрипция не найдена")
            return
            
        print(f"\nУспешно получено {len(transcript)} сегментов")
        
        # Выводим сырые данные
        print_raw_data(transcript)
        
        # Тестируем декодирование
        test_decoding(transcript)
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()
