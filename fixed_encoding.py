from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript_with_fixed_encoding(video_id, language='ru'):
    try:
        # Получаем сырые данные транскрипта
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Пытаемся найти русский транскрипт
        try:
            transcript = transcript_list.find_transcript([language])
            print(f"Найден русский транскрипт")
        except:
            # Если нет русского, пробуем найти переводимый
            for t in transcript_list:
                if t.is_translatable and 'ru' in [lang.language_code for lang in t.translation_languages]:
                    print(f"Найден переводимый транскрипт на {t.language_code}")
                    transcript = t.translate('ru')
                    break
            else:
                print("Не удалось найти русский или переводимый транскрипт")
                return None
        
        # Получаем данные транскрипта
        transcript_data = transcript.fetch()
        
        # Собираем текст с исправлением кодировки
        text_segments = []
        for entry in transcript_data:
            raw_text = entry['text']
            try:
                # Пробуем разные кодировки, начиная с windows-1251
                try:
                    # Сначала пробуем как есть (на случай если уже в UTF-8)
                    if all(ord(c) < 128 for c in raw_text):
                        text_segments.append(raw_text)
                        continue
                        
                    # Пробуем windows-1251
                    fixed_text = raw_text.encode('latin1').decode('windows-1251')
                    text_segments.append(fixed_text)
                except UnicodeError:
                    # Если не сработало, оставляем как есть
                    text_segments.append(raw_text)
            except Exception as e:
                print(f"Ошибка при обработке текста: {str(e)}")
                text_segments.append(raw_text)
        
        # Объединяем все сегменты
        full_text = "\n".join(text_segments)
        
        # Сохраняем в файл с кодировкой UTF-8
        output_file = f'transcript_{video_id}_fixed.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"Транскрипт сохранен в {output_file}")
        return full_text
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

if __name__ == "__main__":
    # Тестируем на видео Simon Sinek
    video_id = "qp0HIF3SfI4"
    text = get_transcript_with_fixed_encoding(video_id, 'ru')
    
    if text:
        print("\nПервые 500 символов:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
