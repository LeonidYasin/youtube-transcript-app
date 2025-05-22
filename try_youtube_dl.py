import youtube_dl
import os
import json

def download_subtitles(video_url, language='ru'):
    """Download subtitles using youtube-dl"""
    ydl_opts = {
        'skip_download': True,  # We only want the subtitles
        'writesubtitles': True,
        'writeautomaticsub': True,  # Include auto-generated subtitles
        'subtitleslangs': [language],  # Language code
        'outtmpl': 'subtitles/%(id)s',  # Output template
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs('subtitles', exist_ok=True)
        
        # Download the subtitles
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
            for lang, subs in {**available_subs, **auto_subs}.items():
                print(f"- {lang}: {len(subs)} formats available")
            
            # Now download the subtitles
            print(f"\nAttempting to download {language} subtitles...")
            ydl.download([video_url])
            
            # Check if subtitles were downloaded
            sub_files = [f for f in os.listdir('subtitles') if f.startswith(video_id)]
            
            if not sub_files:
                print("\nNo subtitle files were downloaded.")
                return None
                
            print("\nDownloaded files:")
            for file in sub_files:
                print(f"- {file}")
                
                # Read and print the first few lines of each file
                try:
                    with open(os.path.join('subtitles', file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\nPreview of {file}:")
                        print(content[:500] + ('...' if len(content) > 500 else ''))
                except Exception as e:
                    print(f"  Could not read {file}: {str(e)}")
            
            return sub_files
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=qp0HIF3SfI4"
    language = 'ru'
    
    print(f"Attempting to download {language} subtitles for: {video_url}")
    result = download_subtitles(video_url, language)
