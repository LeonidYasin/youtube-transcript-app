from youtube_transcript_api import YouTubeTranscriptApi
import json

def analyze_raw_bytes(video_id, language='ru'):
    print(f"Анализ сырых байтов для видео {video_id}")
    print("=" * 80)
    
    try:
        # Получаем транскрипцию
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=[language],
            preserve_formatting=True
        )
        
        if not transcript:
            print("Транскрипция не найдена")
            return
            
        # Берем первый сегмент для анализа
        first_segment = transcript[0]
        text = first_segment.get('text', '')
        
        # Преобразуем текст в байты
        raw_bytes = text.encode('utf-8')
        
        # Выводим информацию о байтах
        print(f"Длина текста: {len(text)} символов")
        print(f"Длина в байтах: {len(raw_bytes)} байт")
        
        # Выводим первые 100 байт в hex
        print("\nПервые 100 байт в hex:")
        hex_bytes = ' '.join(f'{b:02x}' for b in raw_bytes[:100])
        print(hex_bytes)
        
        # Пытаемся декодировать как UTF-8
        print("\nДекодируем как UTF-8:")
        try:
            decoded = raw_bytes.decode('utf-8')
            print(f"Успешно декодировано: {decoded[:100]}...")
        except Exception as e:
            print(f"Ошибка декодирования UTF-8: {str(e)}")
            
        # Проверяем наличие BOM (Byte Order Mark)
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            print("\nОбнаружен BOM (UTF-8 with BOM)")
            
        # Проверяем на другие кодировки
        test_encodings = ['utf-8', 'cp1251', 'cp1252', 'iso-8859-1', 'koi8-r']
        print("\nПроверка кодировок:")
        for enc in test_encodings:
            try:
                decoded = raw_bytes.decode(enc)
                print(f"{enc}: Успешно - {decoded[:50]}...")
            except Exception as e:
                print(f"{enc}: Ошибка - {str(e)}")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    video_id = "qp0HIF3SfI4"
    language = "ru"
    analyze_raw_bytes(video_id, language)
