import yt_dlp
import os
import json

def download_subtitles(video_url, language='ru'):
    """Download subtitles using yt-dlp"""
    ydl_opts = {
        'skip_download': True,  # We only want the subtitles
        'writesubtitles': True,
        'writeautomaticsub': True,  # Include auto-generated subtitles
        'subtitleslangs': [language],  # Language code
        'outtmpl': 'subtitles/%(id)s',  # Output template
        'quiet': False,
        'no_warnings': False,
        'subtitlesformat': 'vtt',  # Use WebVTT format which is more reliable
    }
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs('subtitles', exist_ok=True)
        
        # Download the subtitles
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First get video info
            info_dict = ydl.extract_info(video_url, download=False)
            video_id = info_dict.get('id', None)
            video_title = info_dict.get('title', 'video')
            
            print(f"Title: {video_title}")
            print(f"Video ID: {video_id}")
            
            # Check available subtitles
            available_subs = info_dict.get('subtitles', {})
            auto_subs = info_dict.get('automatic_captions', {})
            
            print("\nAvailable subtitles:")
            all_subs = {**available_subs, **auto_subs}
            for lang, subs in all_subs.items():
                print(f"- {lang}: {len(subs)} formats available")
                for sub in subs:
                    print(f"  - {sub.get('ext', '?')} ({sub.get('name', 'unknown')}): {sub.get('url', 'no URL')[:100]}...")
            
            # If our target language is available, download it
            if language in all_subs:
                print(f"\nFound {language} subtitles!")
                print("Downloading...")
                
                # Now download the subtitles
                ydl.download([video_url])
                
                # Check if subtitles were downloaded
                sub_files = [f for f in os.listdir('subtitles') if f.startswith(video_id)]
                
                if not sub_files:
                    print("\nNo subtitle files were downloaded.")
                    return None
                    
                print("\nDownloaded files:")
                for file in sub_files:
                    file_path = os.path.join('subtitles', file)
                    print(f"- {file} ({os.path.getsize(file_path)} bytes)")
                    
                    # Read and print the first few lines of each file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(f"\nPreview of {file}:")
                            print(content[:500] + ('...' if len(content) > 500 else ''))
                    except Exception as e:
                        print(f"  Could not read {file}: {str(e)}")
                
                return sub_files
            else:
                print(f"\nNo {language} subtitles found in the available formats.")
                return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    language = 'ru'
    
    print(f"Attempting to download {language} subtitles for: {video_url}")
    result = download_subtitles(video_url, language)
