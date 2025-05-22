import yt_dlp
import json

def get_subtitles(video_url, lang='ru'):
    """
    Получает субтитры с YouTube с помощью yt-dlp
    """
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [lang],
        'outtmpl': 'subtitles/%(id)s.%(ext)s',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео
            info = ydl.extract_info(video_url, download=False)
            video_id = info.get('id')
            
            if not video_id:
                print("Не удалось получить ID видео")
                return None
                
            # Пытаемся скачать субтитры
            ydl.download([video_url])
            
            # Проверяем, скачались ли субтитры
            import os
            sub_file = f'subtitles/{video_id}.{lang}.vtt'
            if os.path.exists(sub_file):
                with open(sub_file, 'r', encoding='utf-8') as f:
                    subtitles = f.read()
                
                # Удаляем заголовки VTT
                subtitles = '\n'.join(subtitles.split('\n')[3:])
                
                # Сохраняем в текстовый файл
                txt_file = f'transcript_{video_id}_{lang}.txt'
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(subtitles)
                
                print(f"Субтитры сохранены в {txt_file}")
                return subtitles
            else:
                print("Не удалось найти файл субтитров")
                return None
                
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
