import yt_dlp
import json
from pathlib import Path

def test_yt_dlp():
    video_id = "tw9USlQh6jw"
    output_dir = Path("temp")
    output_dir.mkdir(exist_ok=True)
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['ru'],
        'quiet': True,
        'no_warnings': True,
        'outtmpl': str(output_dir / '%(id)s'),
        'verbose': True  # Включаем подробный вывод
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nDownloading subtitles for video {video_id}")
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
            
            print("\nAvailable subtitles:")
            print("Manual subtitles:", info.get('subtitles', {}))
            print("Auto-generated subtitles:", info.get('automatic_captions', {}))
            
            # Try to download subtitles
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            
            # Check if subtitles file was created
            subtitle_file = output_dir / f"{video_id}.ru.vtt"
            if subtitle_file.exists():
                print(f"\nSuccessfully downloaded subtitles to {subtitle_file}")
                print("\nFirst 1000 chars of subtitle file:")
                print(subtitle_file.read_text(encoding='utf-8')[:1000])
            else:
                print(f"\nSubtitle file {subtitle_file} not found")
                
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_yt_dlp()
