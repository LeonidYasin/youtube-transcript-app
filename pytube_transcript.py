from pytube import YouTube
import os

def get_subtitles(video_url, lang='ru'):
    try:
        # Создаем объект YouTube
        yt = YouTube(video_url)
        
        # Получаем доступные субтитры
        caption = yt.captions.get_by_language_code(lang)
        
        if not caption:
            print(f"Субтитры на языке '{lang}' не найдены")
            print("Доступные языки:")
            for code in yt.captions:
                print(f"- {code.code}: {code.name}")
            return None
        
        # Получаем субтитры в формате srt
        subtitles = caption.generate_srt_captions()
        
        # Сохраняем в файл
        video_id = yt.video_id
        output_file = f"transcript_{video_id}_{lang}.srt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(subtitles)
        
        print(f"Субтитры сохранены в {output_file}")
        
        # Конвертируем в текстовый формат
        txt_file = f"transcript_{video_id}_{lang}.txt"
        with open(output_file, 'r', encoding='utf-8') as f_in, \
             open(txt_file, 'w', encoding='utf-8') as f_out:
            # Пропускаем строки с временными метками и номерами
            lines = f_in.readlines()
            text_lines = [line.strip() for i, line in enumerate(lines) 
                        if i % 4 == 2]  # Берем только строки с текстом
            f_out.write('\n'.join(text_lines))
        
        print(f"Текст субтитров сохранен в {txt_file}")
        
        # Возвращаем текст субтитров
        with open(txt_file, 'r', encoding='utf-8') as f:
            return f.read()
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

if __name__ == "__main__":
    # Тестируем на видео Simon Sinek
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    subtitles = get_subtitles(video_url, 'ru')
    
    if subtitles:
        print("\nПервые 500 символов субтитров:")
        print("-" * 50)
        print(subtitles[:500])
        print("-" * 50)
